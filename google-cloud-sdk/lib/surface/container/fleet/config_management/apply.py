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
"""The command to update Config Management Feature."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import apitools
from googlecloudsdk import api_lib
from googlecloudsdk import core
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet import resources
from googlecloudsdk.command_lib.container.fleet.config_management import command
from googlecloudsdk.command_lib.container.fleet.config_management import utils
from googlecloudsdk.command_lib.container.fleet.features import base as fleet_base
from googlecloudsdk.command_lib.container.fleet.membershipfeatures import base as mf_base
from googlecloudsdk.command_lib.container.fleet.membershipfeatures import convert

# Pull out the example text so the example command can be one line without the
# py linter complaining. The docgen tool properly breaks it into multiple lines.
EXAMPLES = r"""
    To apply the [fleet-default membership configuration](https://cloud.google.com/kubernetes-engine/fleet-management/docs/manage-features)
    to `MEMBERSHIP_NAME`, run:

    $ {command} --membership=MEMBERSHIP_NAME --origin=FLEET

    To apply a membership configuration as a YAML file, prepare
    [apply-spec.yaml](https://cloud.google.com/anthos-config-management/docs/reference/gcloud-apply-fields#example_gcloud_apply_spec) then run:

      $ {command} --membership=MEMBERSHIP_NAME --config=APPLY-SPEC.YAML --version=VERSION
"""


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
@base.DefaultUniverseOnly
class Apply(fleet_base.UpdateCommand, mf_base.UpdateCommand, command.Common):
  """Update a Config Management feature spec.

  Update a membership configuration for the Config Management feature in a
  fleet. This command errors if the Config Management feature is not enabled on
  the fleet.
  """

  detailed_help = {'EXAMPLES': EXAMPLES}

  feature_name = utils.CONFIG_MANAGEMENT_FEATURE_NAME
  mf_name = utils.CONFIG_MANAGEMENT_FEATURE_NAME

  @classmethod
  def Args(cls, parser):
    resources.AddMembershipResourceArg(parser)
    spec_group = parser.add_group(
        required=True,
        mutex=True,
        help=('Update the membership configuration either to the [fleet-default'
              ' membership configuration]('
              'https://cloud.google.com/kubernetes-engine/fleet-management/docs/manage-features)'
              ' with `--origin` or to a user-provided configuration with'
              ' `--config` and `--version`.'),
    )
    spec_group.add_argument(
        '--origin',
        choices=['FLEET'],
        help=('Updates the configuration of the target membership to the'
              ' current [fleet-default membership configuration]('
              'https://cloud.google.com/kubernetes-engine/fleet-management/docs/manage-features).'
              ' Errors if fleet-default membership configuration is not'
              ' enabled; see the `enable` command for more details.'),
    )
    config_group = spec_group.add_group(
        help=('Provide the entire membership configuration to update with'
              ' `--config` and `--version`.')
    )
    config_group.add_argument(
        '--config',
        required=True,
        help=('Path to YAML file that contains the configuration to update the'
              ' target membership to.'
              ' The file accepts the [following fields]('
              'https://cloud.google.com/anthos-config-management/docs/reference'
              '/gcloud-apply-fields).'),
    )
    config_group.add_argument(
        '--version',
        help=('Version of Config Management.'
              ' Equivalent to the [`spec.version`]('
              'https://cloud.google.com/anthos-config-management/docs/reference'
              '/gcloud-apply-fields#common)'
              ' field in the `--config` file.'
              ' Provides `--config` with a version in the absence of'
              ' `spec.version`.'
              ' Cannot specify this flag without `--config`; cannot set both'
              ' this flag and `spec.version`.'
              ' See [`spec.version`]('
              'https://cloud.google.com/anthos-config-management/docs/reference'
              '/gcloud-apply-fields#common)'
              ' for more details.')
    )

  def Run(self, args):
    # Initialize and defend against more than 1 call to Run.
    self.__feature_cache = None

    self.membership = fleet_base.ParseMembership(
        args, prompt=True, autoselect=True, search=True
    )
    feature_spec = self.messages.MembershipFeatureSpec()
    if args.origin:
      feature_spec.origin = self.messages.Origin(
          type=self.messages.Origin.TypeValueValuesEnum.FLEET
      )
    else:
      cm = self.parse_config_management(args.config)
      if cm.version and args.version:
        raise core.exceptions.Error(
            'Cannot set version in multiple flags: --version={} and the version'
            ' field in --config has value {}'.format(args.version, cm.version)
        )
      if args.version:
        cm.version = args.version
      if (not cm.version and
          cm.management !=
          self.messages.ConfigManagementMembershipSpec.ManagementValueValuesEnum.MANAGEMENT_AUTOMATIC):
        cm.version = self._get_backfill_version(self.membership)
      feature_spec.configmanagement = cm
    self._update_membership(feature_spec)

  # Not strictly necessary yet, but helps communicate that we only GetFeature
  # once per execution.
  def _get_feature_cache(self):
    """Gets the Config Management feature at most once per command execution.

    Returns:
      Cached Config Management feature.
    """
    if self.__feature_cache is None:
      # Raises a comprehensible error if feature not enabled.
      self.__feature_cache = self.GetFeature()
    return self.__feature_cache

  def _get_backfill_version(self, membership):
    """Get the value the version field in FeatureSpec should be set to.

    Args:
      membership: The full membership  name whose Spec will be backfilled.

    Returns:
      version: A string denoting the version field in MembershipConfig
    Raises: Error, if retrieving FeatureSpec of FeatureState fails
    """
    f = self._get_feature_cache()
    return utils.get_backfill_version_from_feature(f, membership)

  def _update_membership(self, feature_spec):
    """Update the spec of the target membership to feature_spec.

    Args:
      feature_spec: gkehub API MembershipFeatureSpec to update to.

    Returns:
      Updated feature or membership feature, for projects migrated to v2 by Hub.
    """
    try:
      if not feature_spec.origin:
        membershipfeature = convert.ToV2MembershipFeature(
            self, self.membership, self.mf_name, feature_spec
        )
        return self.UpdateV2(self.membership, ['spec'], membershipfeature)
      else:
        return self.Update(['membership_specs'], self.messages.Feature(
            membershipSpecs=self.hubclient.ToMembershipSpecs({
                self.membership: feature_spec
            })
        ))
    except apitools.base.py.exceptions.HttpError as e:
      raise api_lib.util.exceptions.HttpException(e, '{message}')
