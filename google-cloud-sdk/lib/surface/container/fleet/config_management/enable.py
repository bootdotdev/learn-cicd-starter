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
"""The command to enable Config Management feature."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import apitools
from googlecloudsdk import api_lib
from googlecloudsdk import core
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet.config_management import command
from googlecloudsdk.command_lib.container.fleet.features import base as features_base
import six


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Enable(features_base.EnableCommand,
             features_base.UpdateCommand,
             command.Common):
  """Enable Config Management feature.

  Enables the Config Management feature in a fleet.
  Without any flags, this command no-ops if the feature is already enabled.
  This command can also enable the feature with a [fleet-default membership
  configuration](https://cloud.google.com/kubernetes-engine/fleet-management/docs/manage-features)
  for Config Sync.

  ## EXAMPLES

  To enable the Config Management feature, run:

    $ {command}

  To enable the Config Management feature with a fleet-default membership
  configuration for Config Sync, run:

    $ {command} --fleet-default-member-config=config.yaml
  """

  feature_name = 'configmanagement'

  @classmethod
  def Args(cls, parser):
    parser.add_argument(
        '--fleet-default-member-config',
        help=('Path to YAML file that contains the [fleet-default membership'
              ' configuration]('
              'https://cloud.google.com/kubernetes-engine/fleet-management/docs'
              '/manage-features) to enable with a new feature.'
              ' This file shares the syntax of the `--config` flag on the'
              ' `apply` command: see recognized fields [here]('
              'https://cloud.google.com/kubernetes-engine/enterprise/config-sync/docs/reference/gcloud-apply-fields).'
              ' Errors if the Policy Controller or Hierarchy Controller field'
              ' is set.'
              ' This flag will also enable or update the fleet-default'
              ' membership configuration on an existing feature.'
              ' See the `apply` command for how to sync a membership to the'
              ' fleet-default membership configuration.')
    )

  def Run(self, args):
    try:
      _ = self.enable_feature_with_fdc(args)
    except apitools.base.py.exceptions.HttpError as e:
      # Do not show stack trace to user.
      raise api_lib.util.exceptions.HttpException(e, error_format='{message}')

  def enable_feature_with_fdc(self, args):
    """Enable feature and fleet-default membership configuration, if specified.

    Args:
      args: Command arguments.
    Returns:
      Enabled or updated GKE Hub Feature.
    """
    feature = self.messages.Feature()
    if args.fleet_default_member_config:
      spec = self.parse_config_management(args.fleet_default_member_config)
      feature.fleetDefaultMemberConfig = (
          self.messages.CommonFleetDefaultMemberConfigSpec(
              configmanagement=spec
          )
      )
      try:
        return self.Update(['fleet_default_member_config'], feature)
      except core.exceptions.Error as e:
        if six.text_type(e) != six.text_type(self.FeatureNotEnabledError()):
          raise
    return self.Enable(feature)
