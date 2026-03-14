# -*- coding: utf-8 -*- #
# Copyright 2022 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The command to get the status of Config Management Feature."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.container.fleet import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet import api_util
from googlecloudsdk.command_lib.container.fleet.config_management import utils
from googlecloudsdk.command_lib.container.fleet.features import base as feature_base
from googlecloudsdk.core import log


NA = 'NA'

DETAILED_HELP = {
    'EXAMPLES': """\
   Print the status of the Config Management feature:

    $ {command}

    Name            | Status | Last_Synced_Token | Sync_Branch | Last_Synced_Time              | Policy_Controller | Hierarchy_Controller | Version | Upgrades | Synced_To_Fleet_Default
    --------------- | ------ | ----------------- | ----------- | ----------------------------- | ----------------- | -------------------- | ------- | -------- | ----------------------------
    managed-cluster | SYNCED | 2945500b7f        | acme        | 2020-03-23 11:12:31 -0700 PDT | NA                | NA                   | 1.18.3  | auto     | FLEET_DEFAULT_NOT_CONFIGURED


  View the status for the cluster named `managed-cluster-a`:

    $ {command} --flatten=acm_status --filter="acm_status.name:managed-cluster-a"

  Use a regular expression to list status for multiple clusters:

    $ {command} --flatten=acm_status --filter="acm_status.name ~ managed-cluster.*"

  List all clusters where current Config Sync `Status` is `SYNCED`:

    $ {command} --flatten=acm_status --filter="acm_status.config_sync:SYNCED"

  List all the clusters where sync_branch is `v1` and current Config Sync
  `Status` is not `SYNCED`:

    $ {command} --flatten=acm_status --filter="acm_status.sync_branch:v1 AND -acm_status.config_sync:SYNCED"
  """,
}


class ConfigmanagementFeatureState(object):
  """Feature state class stores ACM status."""

  def __init__(self, cluster_name):
    self.name = cluster_name
    self.config_sync = NA
    self.last_synced_token = NA
    self.last_synced = NA
    self.sync_branch = NA
    self.policy_controller_state = NA
    self.hierarchy_controller_state = NA
    self.version = NA
    self.upgrades = NA
    self.synced_to_fleet_default = NA

  def update_sync_state(self, fs):
    """Update config_sync state for the membership that has ACM installed.

    Args:
      fs: ConfigManagementFeatureState
    """
    if (
        fs.configSyncState is None
        or fs.configSyncState.state.name != 'CONFIG_SYNC_INSTALLED'
    ):
      return

    if fs.configSyncState.syncState:
      if fs.configSyncState.syncState.syncToken:
        self.last_synced_token = fs.configSyncState.syncState.syncToken[:7]
      self.last_synced = fs.configSyncState.syncState.lastSyncTime
      if has_config_sync_git(fs):
        self.sync_branch = fs.membershipSpec.configSync.git.syncBranch

  def update_policy_controller_state(self, md):
    """Update policy controller state for the membership that has ACM installed.

    Args:
      md: MembershipFeatureState
    """
    # Also surface top-level Feature Authorizer errors.
    if md.state.code.name != 'OK':
      self.policy_controller_state = 'ERROR: {}'.format(md.state.description)
      return
    fs = md.configmanagement
    if not (
        fs.policyControllerState and fs.policyControllerState.deploymentState
    ):
      self.policy_controller_state = NA
      return
    pc_deployment_state = fs.policyControllerState.deploymentState
    expected_deploys = {
        'GatekeeperControllerManager': (
            pc_deployment_state.gatekeeperControllerManagerState
        )
    }
    if (
        fs.membershipSpec
        and fs.membershipSpec.version
        and fs.membershipSpec.version > '1.4.1'
    ):
      expected_deploys['GatekeeperAudit'] = pc_deployment_state.gatekeeperAudit
    for deployment_name, deployment_state in expected_deploys.items():
      if not deployment_state:
        continue
      elif deployment_state.name != 'INSTALLED':
        self.policy_controller_state = '{} {}'.format(
            deployment_name, deployment_state
        )
        return
      self.policy_controller_state = deployment_state.name

  def update_hierarchy_controller_state(self, fs):
    """Update hierarchy controller state for the membership that has ACM installed.

    The PENDING state is set separately after this logic. The PENDING state
    suggests the HC part in feature_spec and feature_state are inconsistent, but
    the HC status from feature_state is not ERROR. This suggests that HC might
    be still in the updating process, so we mark it as PENDING

    Args:
      fs: ConfigmanagementFeatureState
    """
    if not (fs.hierarchyControllerState and fs.hierarchyControllerState.state):
      self.hierarchy_controller_state = NA
      return
    hc_deployment_state = fs.hierarchyControllerState.state

    hnc_state = 'NOT_INSTALLED'
    ext_state = 'NOT_INSTALLED'
    if hc_deployment_state.hnc:
      hnc_state = hc_deployment_state.hnc.name
    if hc_deployment_state.extension:
      ext_state = hc_deployment_state.extension.name
    # partial mapping from ('hnc_state', 'ext_state') to 'HC_STATE',
    # ERROR, PENDING, NA states are identified separately
    deploys_to_status = {
        ('INSTALLED', 'INSTALLED'): 'INSTALLED',
        ('INSTALLED', 'NOT_INSTALLED'): 'INSTALLED',
        ('NOT_INSTALLED', 'NOT_INSTALLED'): NA,
    }
    if (hnc_state, ext_state) in deploys_to_status:
      self.hierarchy_controller_state = deploys_to_status[
          (hnc_state, ext_state)
      ]
    else:
      self.hierarchy_controller_state = 'ERROR'

  def update_pending_state(self, api, feature_spec_mc, feature_state_mc):
    """Update Config Management component states if spec does not match state.

    Args:
      api: GKE Hub API
      feature_spec_mc: MembershipConfig
      feature_state_mc: MembershipConfig
    """
    feature_state_pending = (
        feature_state_mc is None and feature_spec_mc is not None
    )
    if feature_state_pending:
      self.last_synced_token = utils.STATUS_PENDING
      self.last_synced = utils.STATUS_PENDING
      self.sync_branch = utils.STATUS_PENDING
      if self.config_sync == NA:
        self.config_sync = utils.STATUS_PENDING
    if (
        self.policy_controller_state.__str__()
        in ['INSTALLED', 'GatekeeperAudit NOT_INSTALLED', NA]
        and feature_state_pending
    ):
      self.policy_controller_state = utils.STATUS_PENDING

    hc_semantic_copy = (
        lambda hc_spec: hc_spec if hc_spec is not None
        else api.ConfigManagementHierarchyControllerConfig()
    )
    if (
        self.hierarchy_controller_state.__str__() != utils.STATUS_ERROR
        and feature_state_pending
        or hc_semantic_copy(feature_spec_mc.hierarchyController)
        != hc_semantic_copy(feature_state_mc.hierarchyController)
    ):
      self.hierarchy_controller_state = utils.STATUS_PENDING


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Status(feature_base.FeatureCommand, base.ListCommand):
  """Print the status of all clusters with Config Management enabled.

  The `Status` column indicates the status of the Config Sync component.
  `Status` displays `NOT_INSTALLED` when Config Sync is not installed.
  `Status` displays `NOT_CONFIGURED` when Config Sync is installed but git/oci
  is not configured. `Status` displays `SYNCED` when Config Sync is installed
  and git/oci is configured and the last sync was successful. `Status` displays
  `ERROR` when Config Sync encounters errors. `Status` displays `STOPPED` when
  Config Sync stops syncing configs to the cluster. `Status` displays
  `PENDING` when Config Sync has not reached the desired state. Otherwise,
  `Status` displays `UNSPECIFIED`.

  The `Synced_to_Fleet_Default` status indicates whether each membership's
  configuration has been synced with the [fleet-default membership configuration
  ](https://cloud.google.com/kubernetes-engine/fleet-management/docs/manage-features).
  `Synced_to_Fleet_Default` displays `FLEET_DEFAULT_NOT_CONFIGURED` when
  fleet-default membership configuration is not enabled.
  `Synced_to_Fleet_Default` for an individual membership may be `UNKNOWN` if
  configuration has yet to be applied to this membership since enabling
  fleet-default membership configuration.
  See the `enable` and `apply` commands for more details.
  """

  detailed_help = DETAILED_HELP

  feature_name = 'configmanagement'

  @staticmethod
  def Args(parser):
    parser.display_info.AddFormat("""
    multi(acm_status:format='table(
            name:label=Name:sort=1,
            config_sync:label=Status,
            last_synced_token:label="Last_Synced_Token",
            sync_branch:label="Sync_Branch",
            last_synced:label="Last_Synced_Time",
            policy_controller_state:label="Policy_Controller",
            hierarchy_controller_state:label="Hierarchy_Controller",
            version:label="Version",
            upgrades:label="Upgrades",
            synced_to_fleet_default:label="Synced_to_Fleet_Default"
      )' , acm_errors:format=list)
    """)

  def Run(self, _):
    memberships, unreachable = api_util.ListMembershipsFull()
    if unreachable:
      log.warning(
          'Locations {} are currently unreachable. Status '
          'entries may be incomplete'.format(unreachable)
      )
    if not memberships:
      return None
    self.f = self.GetFeature()
    acm_status = []
    acm_errors = []

    self.feature_spec_memberships = {
        util.MembershipPartialName(m): s
        for m, s in self.hubclient.ToPyDict(self.f.membershipSpecs).items()
        if s is not None and s.configmanagement is not None
    }
    feature_state_memberships = {
        util.MembershipPartialName(m): s
        for m, s in self.hubclient.ToPyDict(self.f.membershipStates).items()
    }
    # TODO(b/298461043): Refactor this method so it is more readable.
    for name in memberships:
      name = util.MembershipPartialName(name)
      cluster = ConfigmanagementFeatureState(name)
      cluster.synced_to_fleet_default = self.fleet_default_sync_status(name)
      if name not in feature_state_memberships:
        if name in self.feature_spec_memberships:
          # (b/187846229) Show PENDING if feature spec is aware of
          # this membership name but feature state is not
          cluster.update_pending_state(
              self.messages,
              self.feature_spec_memberships[name],
              None
          )
        acm_status.append(cluster)
        continue
      md = feature_state_memberships[name]
      fs = md.configmanagement
      # (b/153587485) Show FeatureState.code if it's not OK
      # as it indicates an unreachable cluster or a dated syncState.code
      if md.state is None or md.state.code is None:
        cluster.config_sync = 'CODE_UNSPECIFIED'
      elif fs is None:
        cluster.config_sync = utils.STATUS_NOT_INSTALLED
      else:
        # operator errors could occur regardless of the deployment_state
        if has_operator_error(fs):
          append_error(name, fs.operatorState.errors, acm_errors)
        # We should update PoCo state regardless of operator state.
        cluster.update_policy_controller_state(md)
        if not has_operator_state(fs):
          if md.state.code.name != 'OK':
            cluster.config_sync = md.state.code.name
          else:
            cluster.config_sync = 'OPERATOR_STATE_UNSPECIFIED'
        else:
          # Set cluster.upgrades
          if (
              fs.membershipSpec is not None
              and fs.membershipSpec.management is not None
              and fs.membershipSpec.management.name
              == utils.MANAGEMENT_AUTOMATIC
          ):
            cluster.upgrades = utils.UPGRADES_AUTO
          else:
            cluster.upgrades = utils.UPGRADES_MANUAL

          # Set cluster.version
          if fs.membershipSpec is not None:
            cluster.version = fs.membershipSpec.version

          # Set cluster.config_sync
          if fs.configSyncState.state is not None:
            cluster.config_sync = config_sync_state(fs)

          # Set cluster.last_synced_token, cluster.sync_branch and
          # cluster.last_synced_time
          cluster.update_sync_state(fs)

          # Add errors into acm_errors
          if fs.configSyncState.errors:
            append_error(name, fs.configSyncState.errors, acm_errors)
          if has_config_sync_sync_error(fs):
            append_error(name, fs.configSyncState.syncState.errors, acm_errors)

          # Set cluster.hierarchy_controller_state
          cluster.update_hierarchy_controller_state(fs)

          if name in self.feature_spec_memberships:
            cluster.update_pending_state(
                self.messages,
                self.feature_spec_memberships[name].configmanagement,
                fs.membershipSpec,
            )
      acm_status.append(cluster)
    return {'acm_errors': acm_errors, 'acm_status': acm_status}

  def fleet_default_sync_status(self, membership):
    if not self.f.fleetDefaultMemberConfig:
      return 'FLEET_DEFAULT_NOT_CONFIGURED'
    if (membership not in self.feature_spec_memberships or
        self.feature_spec_memberships[membership].origin is None):
      return 'UNKNOWN'
    origin = self.feature_spec_memberships[membership].origin.type
    if origin == self.messages.Origin.TypeValueValuesEnum.FLEET:
      return 'YES'
    if (origin == self.messages.Origin.TypeValueValuesEnum.USER or
        origin == self.messages.Origin.TypeValueValuesEnum.FLEET_OUT_OF_SYNC):
      return 'NO'
    return 'UNKNOWN'


def config_sync_state(fs):
  """Convert state to a string shown to the users.

  Args:
    fs: ConfigManagementFeatureState

  Returns:
    a string shown to the users representing the Config Sync state.
  """

  if (
      fs.configSyncState is not None
      and fs.configSyncState.clusterLevelStopSyncingState is not None
  ):
    if fs.configSyncState.clusterLevelStopSyncingState.name in [
        utils.STATUS_STOPPED,
        utils.STATUS_PENDING,
    ]:
      return fs.configSyncState.clusterLevelStopSyncingState.name

  cs_installation_state = fs.configSyncState.state.name

  if cs_installation_state == 'CONFIG_SYNC_PENDING':
    return utils.STATUS_PENDING

  if cs_installation_state == 'CONFIG_SYNC_INSTALLED':
    if fs.configSyncState and fs.configSyncState.syncState:
      return fs.configSyncState.syncState.code.name
    return utils.STATUS_INSTALLED

  if cs_installation_state == 'CONFIG_SYNC_NOT_INSTALLED':
    return utils.STATUS_NOT_INSTALLED

  if cs_installation_state == 'CONFIG_SYNC_ERROR':
    return utils.STATUS_ERROR

  return 'UNSPECIFIED'


def has_operator_state(fs):
  return fs and fs.operatorState and fs.operatorState.deploymentState


def has_operator_error(fs):
  return fs and fs.operatorState and fs.operatorState.errors


def has_config_sync_sync_error(fs):
  return (
      fs
      and fs.configSyncState
      and fs.configSyncState.syncState
      and fs.configSyncState.syncState.errors
  )


def has_config_sync_git(fs):
  return (
      fs.membershipSpec
      and fs.membershipSpec.configSync
      and fs.membershipSpec.configSync.git
  )


def append_error(cluster, state_errors, acm_errors):
  for error in state_errors:
    acm_errors.append({'cluster': cluster, 'error': error.errorMessage})
