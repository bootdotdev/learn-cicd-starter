# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
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

"""Implementation of create command for Insights dataset config."""

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.storage import insights_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.command_lib.storage.insights.dataset_configs import create_update_util
from googlecloudsdk.command_lib.storage.insights.dataset_configs import log_util
from googlecloudsdk.core import log
from googlecloudsdk.core import properties


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Create(base.Command):
  """Create a new dataset config for Insights."""

  detailed_help = {
      'DESCRIPTION': """
       Create a new dataset config for Insights.
      """,
      'EXAMPLES': """
      To create a dataset config with config name as "my_config" in location
      "us-central1" and project numbers "123456" and "456789" belonging to
      organization number "54321":

         $ {command} my_config --location=us-central1
         --source-projects=123456,456789 --organization=54321 --retention-period-days=1

      To create a dataset config that automatically adds new buckets into
      config:

         $ {command} my_config --location=us-central1
         --source-projects=123456,456789 --organization=54321
         --auto-add-new-buckets --retention-period-days=1
      """,
  }

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'DATASET_CONFIG_NAME',
        type=str,
        help='Provide human readable config name.',
    )
    parser.add_argument(
        '--organization',
        type=int,
        required=True,
        metavar='SOURCE_ORG_NUMBER',
        help='Provide the source organization number.',
    )
    parser.add_argument(
        '--identity',
        type=str,
        metavar='IDENTITY_TYPE',
        choices=['IDENTITY_TYPE_PER_CONFIG', 'IDENTITY_TYPE_PER_PROJECT'],
        default='IDENTITY_TYPE_PER_CONFIG',
        help='The type of service account used in the dataset config.',
    )

    parser.add_argument(
        '--auto-add-new-buckets',
        action='store_true',
        help=(
            'Automatically include any new buckets created if they satisfy'
            ' criteria defined in config settings.'
        ),
    )

    flags.add_dataset_config_location_flag(parser)
    flags.add_dataset_config_create_update_flags(parser)

  def Run(self, args):

    source_projects_list = None
    if args.source_projects is not None:
      source_projects_list = args.source_projects
    elif args.source_projects_file is not None:
      source_projects_list = create_update_util.get_source_configs_list(
          args.source_projects_file, create_update_util.ConfigType.PROJECTS
      )

    source_folders_list = None
    if args.source_folders is not None:
      source_folders_list = args.source_folders
    elif args.source_folders_file is not None:
      source_folders_list = create_update_util.get_source_configs_list(
          args.source_folders_file, create_update_util.ConfigType.FOLDERS
      )

    api_client = insights_api.InsightsApi()

    try:
      dataset_config_operation = api_client.create_dataset_config(
          dataset_config_name=args.DATASET_CONFIG_NAME,
          location=args.location,
          destination_project=properties.VALUES.core.project.Get(),
          organization_scope=args.enable_organization_scope,
          source_projects_list=source_projects_list,
          source_folders_list=source_folders_list,
          organization_number=args.organization,
          include_buckets_name_list=args.include_bucket_names,
          include_buckets_prefix_regex_list=args.include_bucket_prefix_regexes,
          exclude_buckets_name_list=args.exclude_bucket_names,
          exclude_buckets_prefix_regex_list=args.exclude_bucket_prefix_regexes,
          include_source_locations=args.include_source_locations,
          exclude_source_locations=args.exclude_source_locations,
          auto_add_new_buckets=args.auto_add_new_buckets,
          retention_period=args.retention_period_days,
          activity_data_retention_period=args.activity_data_retention_period_days,
          identity_type=args.identity,
          description=args.description,
      )
      log_util.dataset_config_operation_started_and_status_log(
          'Create', args.DATASET_CONFIG_NAME, dataset_config_operation.name
      )
    except apitools_exceptions.HttpBadRequestError:
      log.status.Print(
          'We caught an exception while trying to create the'
          ' dataset-configuration.\nPlease check that the flags are set with'
          ' valid values. For example, config name must start with an'
          " alphanumeric value and only contain '_' as a special character"
      )
      raise
