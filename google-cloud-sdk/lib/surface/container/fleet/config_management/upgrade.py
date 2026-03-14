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

from googlecloudsdk.api_lib.container.fleet import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet import resources
from googlecloudsdk.command_lib.container.fleet.config_management import utils
from googlecloudsdk.command_lib.container.fleet.features import base as features_base
from googlecloudsdk.command_lib.container.fleet.membershipfeatures import base as mf_base
from googlecloudsdk.command_lib.container.fleet.membershipfeatures import convert
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Upgrade(features_base.UpdateCommand, mf_base.UpdateCommand):
  """Upgrade the version of the Config Management feature.

  Upgrade a specified membership to any supported version of the Config
  Management feature.

  ## EXAMPLES

  To upgrade a membership named `MEMBERSHIP_NAME`, run:

    $ {command} --membership=MEMBERSHIP_NAME --version=VERSION
  """

  feature_name = utils.CONFIG_MANAGEMENT_FEATURE_NAME
  mf_name = utils.CONFIG_MANAGEMENT_FEATURE_NAME

  @classmethod
  def Args(cls, parser):
    resources.AddMembershipResourceArg(parser)
    parser.add_argument(
        '--version',
        type=str,
        help='The version of ACM to change to.',
        required=True,
    )

  def Run(self, args):
    f = self.GetFeature()
    new_version = args.version
    membership = features_base.ParseMembership(
        args, prompt=True, autoselect=True, search=True
    )
    _, cluster_v = utils.versions_for_member(f, membership)

    if not self._validate_versions(membership, cluster_v, new_version):
      return
    console_io.PromptContinue(
        'You are about to change the {} feature for membership {} from version'
        ' "{}" to version "{}".'.format(
            self.feature.display_name, membership, cluster_v, new_version
        ),
        throw_if_unattended=True,
        cancel_on_no=True,
    )

    patch = self.messages.MembershipFeatureSpec()
    # If there's an existing spec, copy it to leave the other fields intact.
    for full_name, spec in self.hubclient.ToPyDict(f.membershipSpecs).items():
      if (
          util.MembershipPartialName(full_name)
          == util.MembershipPartialName(membership)
          and spec is not None
      ):
        patch = spec
    if patch.configmanagement is None:
      patch.configmanagement = self.messages.ConfigManagementMembershipSpec()
    patch.configmanagement.version = new_version

    membership_key = membership

    membershipfeature = convert.ToV2MembershipFeature(
        self, membership_key, self.mf_name, patch
    )
    self.UpdateV2(membership_key, ['spec'], membershipfeature)

  def _validate_versions(self, membership, cluster_v, new_v):
    if cluster_v == new_v:
      log.status.Print(
          'Membership {} already has version {} of the {} feature installed.'
          .format(membership, cluster_v, self.feature.display_name)
      )
      return False

    return True
