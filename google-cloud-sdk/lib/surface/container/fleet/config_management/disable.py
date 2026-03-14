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
"""The command to disable Config Management Feature."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet import flags
from googlecloudsdk.command_lib.container.fleet import resources
from googlecloudsdk.command_lib.container.fleet.config_management import utils
from googlecloudsdk.command_lib.container.fleet.features import base as features_base
from googlecloudsdk.command_lib.container.fleet.membershipfeatures import base as membershipfeatures_base
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
class Disable(
    features_base.DisableCommand,
    membershipfeatures_base.DeleteCommandMixin,
    membershipfeatures_base.UpdateCommandMixin,
):
  """Disable the Config Management feature.

  Disable the Config Management feature entirely, or disable specific
  configuration on the feature.

  `{command}` without flags deletes the Config Management feature,
  which unmanages and leaves existing Config Sync installations on membership
  clusters. Running the command without flags exits silently if the feature
  does not exist. Specify flags to disable configuration on parts of the feature
  without deleting it.

  ## EXAMPLES

  To disable the Config Management feature entirely, run:

    $ {command}

  To unmanage Config Sync only on select memberships, run:

    $ {command} --memberships=example-membership-1,example-membership-2
  """

  feature_name = utils.CONFIG_MANAGEMENT_FEATURE_NAME
  mf_name = utils.CONFIG_MANAGEMENT_FEATURE_NAME
  support_fleet_default = True

  @classmethod
  def Args(cls, parser):
    """Adds flags to the command.

    Args:
      parser: googlecloudsdk.calliope.parser_arguments.ArgumentInterceptor,
        Argument parser to add flags to.
    """
    cls.FORCE_FLAG.AddToParser(parser)
    partial_disable_flag_group = parser.add_mutually_exclusive_group()
    cls.FLEET_DEFAULT_MEMBER_CONFIG_FLAG.AddToParser(partial_disable_flag_group)
    membership_disable_group = partial_disable_flag_group.add_group(
        # The help text for this group is required, especially since --uninstall
        # reads better in front of the Membership flags.
        # Otherwise, readers cannot perceive the grouping of
        # Membership-specific flags, and thus may confuse exactly which flags
        # are mutually exclusive with --fleet-default-member-config.
        help=(
            'Membership-specific flags.'
            ' In the absence of `--uninstall`, using either'
            ' `--memberships` or `--all-memberships` removes the entire'
            ' configuration for the specified memberships, which unmanages and'
            ' leaves existing Config Sync installations on the membership'
            ' clusters.'
            ' Unmanagement does not error if the feature is disabled.'
        ),
    )
    membership_disable_group.add_argument(
        '--uninstall',
        action='store_const',
        const=True,
        help="""\
Uninstall any previously-installed and managed Config Sync on the specified
memberships by setting the `enabled`
[field](https://cloud.google.com/kubernetes-engine/enterprise/config-sync/docs/reference/gcloud-apply-fields)
to false. Clears all other configuration for each membership. Does not wait for
the uninstallation to complete. To bypass the confirmation prompt, use
`--force`. Requires the feature to be enabled.

To uninstall Config Sync on select memberships, run:

  $ {command} --uninstall --memberships=example-membership-1,example-membership-2
""",
    )
    memberships_group = membership_disable_group.add_mutually_exclusive_group()
    resources.AddMembershipResourceArg(memberships_group, plural=True)
    flags.ALL_MEMBERSHIPS_FLAG.AddToParser(memberships_group)

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException('{message}')
  def Run(self, args):
    """Executes command logic.

    Disables parts of or the entire feature specified by args.

    Args:
      args: Flags specified in the call. The value associated with each flag
        is stored on an args field that is named after the flag with dashes
        replaced by underscores.
    Returns:
      None. In other words, completes without outputting the disabled or
        partially disabled Feature.
    Raises:
      api_lib.util.exceptions.HttpException: On HTTP errors from API calls,
        raises the exception without details to remove the stack trace.
        `gcloud info --show-log` shows the entire error to users who care.
    """
    if args.fleet_default_member_config:
      self.clear_fleet_default()
      return
    memberships = []
    if args.uninstall or args.memberships or args.all_memberships:
      # Verify Membership existence because otherwise unmanage may succeed for
      # non-existent Memberships.
      memberships = features_base.ParseMembershipsPlural(args,
                                                         prompt=True,
                                                         search=True)
    if args.uninstall:
      # Feature must exist for Config Management Hub controllers to uninstall
      # Config Sync.
      self.GetFeature()
      if not args.force:
        console_io.PromptContinue(
            message=(
                'About to uninstall any previously-installed and managed'
                ' Config Sync on the specified memberships.'
            ),
            cancel_on_no=True,
        )
    for membership in memberships:
      if args.uninstall:
        self.UpdateV2(membership, ['spec'], self.messages_v2.MembershipFeature(
            spec=self.messages_v2.FeatureSpec(
                configmanagement=self.messages_v2.ConfigManagementSpec(
                    configSync=self.messages_v2.ConfigManagementConfigSync(
                        enabled=False,
                    ),
                ),
            ),
        ))
      else:
        self.DeleteV2(membership)
    if not memberships:
      self.Disable(args.force)
