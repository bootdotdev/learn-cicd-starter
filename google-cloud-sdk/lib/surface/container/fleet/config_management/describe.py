# -*- coding: utf-8 -*- #
# Copyright 2025 Google LLC. All Rights Reserved.
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
"""The command to view the Config Management Feature."""

import copy

from googlecloudsdk.api_lib.container.fleet import transforms
from googlecloudsdk.api_lib.container.fleet import util
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet import resources
from googlecloudsdk.command_lib.container.fleet.config_management import utils
from googlecloudsdk.command_lib.container.fleet.features import base as features_base
from googlecloudsdk.command_lib.container.fleet.membershipfeatures import base as membershipfeatures_base
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
class Describe(
    # MembershipFeature must be inherited before Feature so that this class can
    # use the prior's MembershipFeatureResourceName() method.
    membershipfeatures_base.MembershipFeatureCommand,
    features_base.DescribeCommand
):
  """Describe the Config Management feature."""
  feature_name = utils.CONFIG_MANAGEMENT_FEATURE_NAME
  mf_name = utils.CONFIG_MANAGEMENT_FEATURE_NAME


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class DescribeAlpha(Describe):
  """Describe the Config Management feature."""

  detailed_help = {
      'EXAMPLES': """
To describe the entire Config Management feature, run:

  $ {command}

To describe select membership configurations, run:

  $ {command} --memberships=example-membership-1,example-membership-2

To list the membership configurations, run:

  $ {command} --view=list

MEMBERSHIP           | LOCATION    | STATUS | INSTALL_STATE             | STOP_STATE  | SYNC_STATE    | VERSION | SYNCED_TO_FLEET_DEFAULT
-------------------- | ----------- | ------ | ------------------------- | ----------- | ------------- | ------- | ----------------------------
example-membership-1 | asia-east1  | OK     | CONFIG_SYNC_NOT_INSTALLED |             | NOT_INSTALLED |         | FLEET_DEFAULT_NOT_CONFIGURED
example-membership-2 | us-central1 | OK     | CONFIG_SYNC_INSTALLED     | NOT_STOPPED | SYNCED        | 1.22.0  | FLEET_DEFAULT_NOT_CONFIGURED
example-membership-3 | us-central1 | ERROR  | CONFIG_SYNC_INSTALLED     | NOT_STOPPED | ERROR         | 1.21.3  | FLEET_DEFAULT_NOT_CONFIGURED
      """,
  }

  @classmethod
  def Args(cls, parser):
    cls.parser = parser
    view_group = parser.add_group()
    view_group.add_argument(
        '--view',
        help='View of the feature.',
        choices={
            'full': 'Default view. Prints the entire feature.',
            'list': """
List of membership configurations. Default format is a table summary.

The `SYNCED_TO_FLEET_DEFAULT` column may display `UNKNOWN` for any membership
whose configuration has not been updated since the
[fleet-default membership configuration](https://cloud.google.com/kubernetes-engine/fleet-management/docs/manage-features)
enablement.

To view the underlying configurations instead of the table summary for select
memberships, run:

  $ {command} --view=list --format=yaml --memberships=example-membership-1,example-membership-2
            """,
        },
        default='full',
        required=True,
    )
    # Sole purpose of list_group and memberships_group is to add help text.
    list_group = view_group.add_group(
        category=base.LIST_COMMAND_FLAGS,
        help=(
            'List command flags.'
            ' Only specify when `--view=list`.'
            ' Does not include support for `--limit`.'
        ),
    )
    filter_with_examples = copy.deepcopy(base.FILTER_FLAG)
    filter_with_examples.kwargs['help'] = (
        filter_with_examples.kwargs['help'].rstrip() + """

To filter for memberships with an overall status of `ERROR`, use the
``COLUMN~VALUE'' pattern and run:

  $ {command} --view=list --filter=STATUS~ERROR

To filter for memberships that are synced to the
fleet-default membership configuration, run:

  $ {command} --view=list --filter="spec.origin.type.synced_to_fleet_default()~YES"

`SYNCED_TO_FLEET_DEFAULT` is the only column that requires filtering on the
underlying configuration field instead of the column name. An alternative is to
`--sort-by=SYNCED_TO_FLEET_DEFAULT` and filter by eye.

To filter on a configuration field not in the table summary, in this case the
Config Sync repo, run:

  $ {command} --view=list --format=yaml --filter="spec.configmanagement.configSync.git.syncRepo~https://github.com/GoogleCloudPlatform/anthos-config-management-samples.git"
        """
    )
    filter_with_examples.AddToParser(list_group)
    sort_by_with_examples = copy.deepcopy(base.SORT_BY_FLAG)
    sort_by_with_examples.kwargs['help'] = (
        sort_by_with_examples.kwargs['help'].rstrip() + """

The default table summary sorts by `LOCATION` then `MEMBERSHIP`.

To sort the table by `VERSION` instead, run:

  $ {command} --view=list --sort-by=VERSION

To sort by a configuration field not in the table summary, in this case the
Config Sync repo, and print its values in a table, run:

  $ {command} --view=list --sort-by="spec.configmanagement.configSync.git.syncRepo" --format="table(MEMBERSHIP,LOCATION,spec.configmanagement.configSync.git.syncRepo:label=REPO)"
        """
    )
    sort_by_with_examples.AddToParser(list_group)
    memberships_group = parser.add_group(
        help=(
            'Memberships to print configurations for.'
            ' Errors if a specified membership does not have a configuration'
            ' for this feature.'
        )
    )
    resources.AddMembershipResourceArg(memberships_group, plural=True)

  @staticmethod
  def enforce_flag_combinations(args):
    if (args.filter or args.sort_by) and args.view != 'list':
      raise exceptions.Error(
          '--filter and --sort-by can only be specified when --view=list.'
      )

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException('{message}')
  def Run(self, args):
    self.args = args
    self.enforce_flag_combinations(args)
    feature = self.GetFeature()
    if args.memberships:
      # Verify the specified Memberships exist to distinguish them from
      # Memberships that have no specs in error messages.
      memberships = features_base.ParseMembershipsPlural(args, search=True)
      self.filter_feature_for_memberships(feature, memberships)
    if args.view == 'list':
      # Limit transforms to --view=list for simplicity; relax if necessary.
      self.parser.display_info.AddTransforms(transforms.get_transforms(
          self.hubclient, feature.fleetDefaultMemberConfig is not None,
      ))
      self.parser.display_info.AddFormat("""table(
          name.segment(-3):label=MEMBERSHIP:sort=2,
          name.segment(-5):label=LOCATION:sort=1,
          state.state.code:label=STATUS,
          state.configmanagement.configSyncState.state:label=INSTALL_STATE,
          state.configmanagement.configSyncState.clusterLevelStopSyncingState:label=STOP_STATE,
          state.configmanagement.configSyncState.syncState.code:label=SYNC_STATE,
          state.configmanagement.membershipSpec.version:label=VERSION,
          spec.origin.type.synced_to_fleet_default():label=SYNCED_TO_FLEET_DEFAULT
      )""")
      return self.construct_membership_features_list(feature)
    return feature

  def construct_membership_features_list(self, feature):
    if feature.unreachable:
      log.warning('Membership configuration list may be incomplete.'
                  ' Unreachable locations: %s', feature.unreachable)
    if not feature.membershipSpecs:
      return []
    states = {}
    if feature.membershipStates:
      states = {
          util.MembershipPartialName(entry.key): entry.value
          for entry in feature.membershipStates.additionalProperties
      }
    project_id = self.Project(number=False)
    project_number = self.Project(number=True)
    return [
        # Mimic v2 MembershipFeature. Leaves room for alternate
        # ListMembershipFeatures API call implementation. Uses dictionary
        # instead of generated API message class to avoid potential v1 vs. v2
        # configuration discrepancy errors. (Since we don't promise the output
        # of --view=list passes into other commands as input, any v1 vs. v2
        # discrepancy is forgivable.)
        {
            # Use project name instead of number for readability, to follow
            # resource name convention, and to match the v2 API output for
            # MembershipFeature. Do not use functions like
            # util.MembershipFeatureResourceName() that parse the resources
            # REGISTRY due to poor performance, which doesn't scale with the
            # number of Memberships.
            'name': self.MembershipFeatureResourceName(
                entry.key.replace(
                    f'projects/{project_number}/',
                    f'projects/{project_id}/',
                    1
                )
            ),
            'spec': entry.value,
            **(
                {'state': states[util.MembershipPartialName(entry.key)]}
                if util.MembershipPartialName(entry.key) in states
                else {}
            )
        }
        for entry in feature.membershipSpecs.additionalProperties
    ]

  def Epilog(self, resources_were_displayed):
    # Reference Epilog method on ListCommand.
    if not resources_were_displayed and self.args.view == 'list':
      log.status.Print('Listed 0 items.')
