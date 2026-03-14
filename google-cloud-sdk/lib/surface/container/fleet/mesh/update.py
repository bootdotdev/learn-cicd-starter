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
"""The command to update Service Mesh Feature."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.container.fleet import util
from googlecloudsdk.calliope import actions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.anthos.common import file_parsers
from googlecloudsdk.command_lib.container.fleet import resources
from googlecloudsdk.command_lib.container.fleet.features import base as features_base
from googlecloudsdk.command_lib.container.fleet.membershipfeatures import base as mf_base
from googlecloudsdk.command_lib.container.fleet.mesh import utils


# LINT.IfChange(update_v2)
def _RunUpdateV2(cmd, args):
  """Runs the update command implementation that is common across release tracks.

  For membership level spec update, we will use v2alpha API to directly update
  the membership feature resource.

  Args:
    cmd: the release track specific command
    args: the args passed to the command
  """

  memberships = []
  resource = False
  update_mask = []

  # Deprecated non-resource arg
  if args.IsKnownAndSpecified('membership'):
    resource = False
    memberships = utils.ParseMemberships(args)
  elif args.fleet_default_member_config is None:
    resource = True
    memberships = features_base.ParseMembershipsPlural(
        args, prompt=True, search=True
    )

  for membership in memberships:
    if not resource:
      membership = cmd.MembershipResourceName(membership)

    patch_v2 = cmd.messages_v2.FeatureSpec()

    try:
      existing_membership_feature = cmd.GetMembershipFeature(membership)
    except apitools_exceptions.HttpNotFoundError:
      existing_membership_feature = cmd.messages_v2.MembershipFeature()

    if existing_membership_feature.spec:
      patch_v2 = existing_membership_feature.spec

    if not patch_v2.servicemesh:
      patch_v2.servicemesh = cmd.messages_v2.ServiceMeshSpec()

    if hasattr(args, 'origin') and args.origin is not None:
      if args.origin == 'fleet':
        patch_v2.origin = cmd.messages_v2.Origin(
            type=cmd.messages_v2.Origin.TypeValueValuesEnum('FLEET')
        )

    if hasattr(args, 'management') and args.management is not None:
      management_v2 = (
          cmd.messages_v2.ServiceMeshSpec.ManagementValueValuesEnum(
              'MANAGEMENT_MANUAL'))
      if args.management == 'automatic':
        management_v2 = (
            cmd.messages_v2.ServiceMeshSpec.ManagementValueValuesEnum(
                'MANAGEMENT_AUTOMATIC'))
      if args.management == 'not_installed':
        management_v2 = (
            cmd.messages_v2.ServiceMeshSpec.ManagementValueValuesEnum(
                'MANAGEMENT_NOT_INSTALLED'))
      patch_v2.servicemesh.management = management_v2

    if args.control_plane is not None:
      control_plane_v2 = (
          cmd.messages_v2.ServiceMeshSpec.ControlPlaneValueValuesEnum(
              'MANUAL'))
      if args.control_plane == 'automatic':
        control_plane_v2 = (
            cmd.messages_v2.ServiceMeshSpec.ControlPlaneValueValuesEnum(
                'AUTOMATIC'))
      elif args.control_plane == 'unspecified':
        control_plane_v2 = (
            cmd.messages_v2.ServiceMeshSpec.ControlPlaneValueValuesEnum(
                'CONTROL_PLANE_MANAGEMENT_UNSPECIFIED'))
      patch_v2.servicemesh.controlPlane = control_plane_v2

    if hasattr(args, 'config_api') and args.config_api is not None:
      config_api = (
          cmd.messages_v2.ServiceMeshSpec.ConfigApiValueValuesEnum(
              'CONFIG_API_UNSPECIFIED'
          )
      )
      if args.config_api == 'istio':
        config_api = (
            cmd.messages_v2.ServiceMeshSpec.ConfigApiValueValuesEnum(
                'CONFIG_API_ISTIO'
            )
        )
      if args.config_api == 'gateway':
        config_api = (
            cmd.messages_v2.ServiceMeshSpec.ConfigApiValueValuesEnum(
                'CONFIG_API_GATEWAY'
            )
        )
      patch_v2.servicemesh.configApi = config_api

    cmd.UpdateV2(
        membership, ['spec'], cmd.messages_v2.MembershipFeature(spec=patch_v2)
    )

  f = cmd.messages.Feature()

  if args.fleet_default_member_config:
    # Load config YAML file.
    loaded_config = file_parsers.YamlConfigFile(
        file_path=args.fleet_default_member_config,
        item_type=utils.FleetDefaultMemberConfigObject,
    )

    # Create new service mesh feature spec.
    member_config = utils.ParseFleetDefaultMemberConfigV2(
        loaded_config, cmd.messages
    )
    f.fleetDefaultMemberConfig = (
        cmd.messages.CommonFleetDefaultMemberConfigSpec(mesh=member_config)
    )
    update_mask.append('fleet_default_member_config')

  if update_mask:
    cmd.Update(update_mask, f)
# LINT.ThenChange(:update_v1)


# LINT.IfChange(update_v1)
def _RunUpdate(cmd, args):
  """Runs the update command implementation that is common across release tracks.

  Args:
    cmd: the release track specific command
    args: the args passed to the command
  """

  memberships = []
  resource = False
  update_mask = []

  # Deprecated non-resource arg
  if args.IsKnownAndSpecified('membership'):
    resource = False
    memberships = utils.ParseMemberships(args)
    update_mask = ['membershipSpecs']
  elif args.fleet_default_member_config is None:
    resource = True
    memberships = features_base.ParseMembershipsPlural(
        args, prompt=True, search=True
    )
    update_mask = ['membershipSpecs']

  f = cmd.GetFeature()
  membership_specs = {}
  for membership in memberships:
    if not resource:
      membership = cmd.MembershipResourceName(membership)
    patch = cmd.messages.MembershipFeatureSpec()

    for name, spec in cmd.hubclient.ToPyDict(f.membershipSpecs).items():
      if (
          util.MembershipShortname(name) == util.MembershipShortname(membership)
          and spec
      ):
        patch = spec
    if not patch.mesh:
      patch.mesh = cmd.messages.ServiceMeshMembershipSpec()

    if hasattr(args, 'origin') and args.origin is not None:
      if args.origin == 'fleet':
        patch.origin = cmd.messages.Origin(
            type=cmd.messages.Origin.TypeValueValuesEnum('FLEET')
        )

    if hasattr(args, 'management') and args.management is not None:
      management = (
          cmd.messages.ServiceMeshMembershipSpec.ManagementValueValuesEnum(
              'MANAGEMENT_MANUAL'
          )
      )
      if args.management == 'automatic':
        management = (
            cmd.messages.ServiceMeshMembershipSpec.ManagementValueValuesEnum(
                'MANAGEMENT_AUTOMATIC'
            )
        )
      if args.management == 'not_installed':
        management = (
            cmd.messages_v2.ServiceMeshSpec.ManagementValueValuesEnum(
                'MANAGEMENT_NOT_INSTALLED'))
      patch.mesh.management = management

    if args.control_plane is not None:
      control_plane = (
          cmd.messages.ServiceMeshMembershipSpec.ControlPlaneValueValuesEnum(
              'MANUAL'
          )
      )
      if args.control_plane == 'automatic':
        control_plane = (
            cmd.messages.ServiceMeshMembershipSpec.ControlPlaneValueValuesEnum(
                'AUTOMATIC'
            )
        )
      elif args.control_plane == 'unspecified':
        control_plane = (
            cmd.messages.ServiceMeshMembershipSpec.ControlPlaneValueValuesEnum(
                'CONTROL_PLANE_MANAGEMENT_UNSPECIFIED'
            )
        )
      patch.mesh.controlPlane = control_plane

    if hasattr(args, 'config_api') and args.config_api is not None:
      config_api = (
          cmd.messages.ServiceMeshMembershipSpec.ConfigApiValueValuesEnum(
              'CONFIG_API_UNSPECIFIED'
          )
      )
      if args.config_api == 'istio':
        config_api = (
            cmd.messages.ServiceMeshMembershipSpec.ConfigApiValueValuesEnum(
                'CONFIG_API_ISTIO'
            )
        )
      if args.config_api == 'gateway':
        config_api = (
            cmd.messages.ServiceMeshMembershipSpec.ConfigApiValueValuesEnum(
                'CONFIG_API_GATEWAY'
            )
        )
      patch.mesh.configApi = config_api

    membership_specs[membership] = patch

  f = cmd.messages.Feature(
      membershipSpecs=cmd.hubclient.ToMembershipSpecs(membership_specs)
  )

  if args.fleet_default_member_config:
    # Load config YAML file.
    loaded_config = file_parsers.YamlConfigFile(
        file_path=args.fleet_default_member_config,
        item_type=utils.FleetDefaultMemberConfigObject,
    )

    # Create new service mesh feature spec.
    member_config = utils.ParseFleetDefaultMemberConfig(
        loaded_config, cmd.messages
    )
    f.fleetDefaultMemberConfig = (
        cmd.messages.CommonFleetDefaultMemberConfigSpec(mesh=member_config)
    )
    update_mask.append('fleet_default_member_config')

  cmd.Update(update_mask, f)
# LINT.ThenChange(:update_v2)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(features_base.UpdateCommand, mf_base.UpdateCommand):
  """Update the configuration of the Service Mesh Feature.

  Update the Service Mesh Feature Spec of a membership.

  ## EXAMPLES

  To update the control plane management of comma separated memberships like
  `MEMBERSHIP1,MEMBERSHIP2`, run:

    $ {command} --memberships=MEMBERSHIP1,MEMBERSHIP2
      --control-plane=CONTROL_PLANE
  """

  feature_name = 'servicemesh'
  mf_name = 'servicemesh'

  @staticmethod
  def Args(parser):
    args_group = parser.add_mutually_exclusive_group(required=True)

    args_group.add_argument(
        '--fleet-default-member-config',
        type=str,
        help="""The path to a service-mesh.yaml configuration file.

        To enable the Service Mesh Feature with a fleet-level default
        membership configuration, run:

          $ {command} --fleet-default-member-config=/path/to/service-mesh.yaml""",
    )

    membership_group = args_group.add_group(
        'Component options',
    )

    membership_names_group = membership_group.add_mutually_exclusive_group()
    resources.AddMembershipResourceArg(
        membership_names_group,
        plural=True,
        membership_help=(
            'Membership names to update, separated by commas if '
            'multiple are supplied.'
        ),
    )
    membership_names_group.add_argument(
        '--membership',
        type=str,
        help='Membership name to update.',
        action=actions.DeprecationAction(
            '--membership',
            warn=(
                'The {flag_name} flag is now '
                'deprecated. Please use `--memberships` '
                'instead.'
            ),
        ),
    )

    membership_config_group = membership_group.add_group(required=True)
    membership_config_group.add_argument(
        '--origin',
        choices=['fleet'],
        help='Changing the origin of the membership.',
    )
    membership_controlplane_group = (
        membership_config_group.add_mutually_exclusive_group()
    )

    membership_controlplane_group.add_argument(
        '--config-api',
        choices=['istio', 'gateway'],
        help='The API to use for mesh configuration.',
    )
    membership_controlplane_group.add_argument(
        '--management',
        choices=['automatic', 'manual', 'not_installed'],
        help='The management mode to update to.',
    )
    membership_controlplane_group.add_argument(
        '--control-plane',
        choices=['automatic', 'manual', 'unspecified'],
        help='Control plane management to update to.',
        action=actions.DeprecationAction(
            '--control-plane',
            warn=(
                'The {flag_name} flag is now '
                'deprecated. Please use `--management` '
                'instead. '
                'See https://cloud.google.com/service-mesh/docs/managed/provision-managed-anthos-service-mesh'
            ),
        ),
    )

  def Run(self, args):
    # If the user is using the fleet default config, we will still use the v1
    # Feature API for the update.
    use_fleet_default_config = (
        hasattr(args, 'origin')
        and args.origin == 'fleet'
    )
    if not use_fleet_default_config:
      _RunUpdateV2(self, args)
    else:
      _RunUpdate(self, args)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
class UpdateGA(features_base.UpdateCommand, mf_base.UpdateCommand):
  """Update the configuration of the Service Mesh Feature.

  Update the Service Mesh Feature Spec of a Membership.

  ## EXAMPLES

  To update the control plane management of comma separated Memberships like
  `membership1,membership2`, run:

    $ {command} --memberships=membership1,membership2
      --control-plane=CONTROL_PLANE
  """

  feature_name = 'servicemesh'
  mf_name = 'servicemesh'

  @staticmethod
  def Args(parser):
    args_group = parser.add_mutually_exclusive_group(required=True)

    args_group.add_argument(
        '--fleet-default-member-config',
        type=str,
        help="""The path to a service-mesh.yaml configuration file.

        To enable the Service Mesh Feature with a fleet-level default
        membership configuration, run:

          $ {command} --fleet-default-member-config=/path/to/service-mesh.yaml""",
    )

    membership_group = args_group.add_group()

    membership_names_group = membership_group.add_mutually_exclusive_group()
    resources.AddMembershipResourceArg(
        membership_names_group,
        plural=True,
        membership_help=(
            'Membership names to update, separated by commas if '
            'multiple are supplied.'
        ),
    )

    membership_configs_group = membership_group.add_group(required=True)
    membership_configs_group.add_argument(
        '--origin',
        choices=['fleet'],
        help='Changing the origin of the membership.',
    )
    membership_controlplane_group = (
        membership_configs_group.add_mutually_exclusive_group()
    )

    membership_controlplane_group.add_argument(
        '--config-api',
        choices=['istio', 'gateway'],
        help='The API to use for mesh configuration.',
    )
    membership_controlplane_group.add_argument(
        '--management',
        choices=['automatic', 'manual'],
        help='The management mode to update to.',
    )
    membership_controlplane_group.add_argument(
        '--control-plane',
        choices=['automatic', 'manual', 'unspecified'],
        help='Control plane management to update to.',
        action=actions.DeprecationAction(
            '--control-plane',
            warn=(
                'The {flag_name} flag is now '
                'deprecated. Please use `--management` '
                'instead. '
                'See https://cloud.google.com/service-mesh/docs/managed/provision-managed-anthos-service-mesh'
            ),
        ),
    )

  def Run(self, args):
    # If the user is using the fleet default config, we will still use the v1
    # Feature API for the update.
    use_fleet_default_config = (
        hasattr(args, 'origin')
        and args.origin == 'fleet'
    )
    if not use_fleet_default_config:
      _RunUpdateV2(self, args)
    else:
      _RunUpdate(self, args)
