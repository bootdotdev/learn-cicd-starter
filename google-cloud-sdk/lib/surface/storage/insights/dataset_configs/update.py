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

"""Implementation of update command for Insights dataset config."""

from googlecloudsdk.api_lib.storage import insights_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.command_lib.storage.insights.dataset_configs import create_update_util
from googlecloudsdk.command_lib.storage.insights.dataset_configs import log_util
from googlecloudsdk.command_lib.storage.insights.dataset_configs import resource_args
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Update(base.Command):
  """Updates a dataset config for Insights."""

  detailed_help = {
      'DESCRIPTION': """
      Update a dataset config for Insights.
      """,
      'EXAMPLES': """

      To update the description for a dataset config "my_config" in
      location "us-central1":

          $ {command} my_config --location=us-central1 --description="a user provided description"

      To update the same dataset config with fully specified name:

          $ {command} projects/foo/locations/us-central1/datasetConfigs/my_config

      To update the retention period days for the dataset config "my_config" in
      location "us-central1":

          $ {command} my_config --location=us-central1
          --retention-period-days=20
      """,
  }

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--auto-add-new-buckets',
        choices=['true', 'false'],
        help=(
            'Automatically include any new buckets created if they satisfy'
            ' criteria defined in config settings.'
        ),
    )

    resource_args.add_dataset_config_resource_arg(parser, 'to update')
    flags.add_dataset_config_create_update_flags(parser, is_update=True)

  def _get_source_projects_list(self, args):
    if args.source_projects is not None:
      return args.source_projects
    elif args.source_projects_file is not None:
      return create_update_util.get_source_configs_list(
          args.source_projects_file, create_update_util.ConfigType.PROJECTS
      )
    return None

  def _get_source_folders_list(self, args):
    if args.source_folders is not None:
      return args.source_folders
    elif args.source_folders_file is not None:
      return create_update_util.get_source_configs_list(
          args.source_folders_file, create_update_util.ConfigType.FOLDERS
      )
    return None

  def _get_auto_add_new_buckets(self, args):
    if args.auto_add_new_buckets is not None:
      if args.auto_add_new_buckets == 'true':
        return True
      elif args.auto_add_new_buckets == 'false':
        return False
    return None

  def Run(self, args):
    client = insights_api.InsightsApi()
    dataset_config_relative_name = (
        args.CONCEPTS.dataset_config.Parse().RelativeName()
    )

    if args.retention_period_days is not None:
      if args.retention_period_days > 0:
        message = (
            'You are about to change retention period for dataset config: {}'
            .format(dataset_config_relative_name)
        )
        console_io.PromptContinue(
            message=message, throw_if_unattended=True, cancel_on_no=True
        )
      else:
        raise ValueError('retention-period-days value must be greater than 0')

    source_projects_list = self._get_source_projects_list(args)
    source_folders_list = self._get_source_folders_list(args)
    new_scope = create_update_util.get_new_source_config(
        args.enable_organization_scope,
        source_projects_list,
        source_folders_list,
    )

    if new_scope is not None:
      existing_scope = create_update_util.get_existing_source_config(
          dataset_config_relative_name, client
      )
      message = (
          'You are about to change scope of dataset config:'
          f' {dataset_config_relative_name} from {existing_scope} to'
          f' {new_scope}. Refer'
          ' https://cloud.google.com/storage/docs/insights/datasets#dataset-config'
          ' for more details.'
      )
      console_io.PromptContinue(
          message=message, throw_if_unattended=True, cancel_on_no=True
      )

    auto_add_new_buckets = self._get_auto_add_new_buckets(args)

    update_dataset_config_operation = client.update_dataset_config(
        dataset_config_relative_name,
        organization_scope=args.enable_organization_scope,
        source_projects_list=source_projects_list,
        source_folders_list=source_folders_list,
        include_buckets_name_list=args.include_bucket_names,
        include_buckets_prefix_regex_list=args.include_bucket_prefix_regexes,
        exclude_buckets_name_list=args.exclude_bucket_names,
        exclude_buckets_prefix_regex_list=args.exclude_bucket_prefix_regexes,
        include_source_locations=args.include_source_locations,
        exclude_source_locations=args.exclude_source_locations,
        auto_add_new_buckets=auto_add_new_buckets,
        retention_period=args.retention_period_days,
        activity_data_retention_period=args.activity_data_retention_period_days,
        description=args.description,
    )

    log_util.dataset_config_operation_started_and_status_log(
        'Update',
        dataset_config_relative_name,
        update_dataset_config_operation.name,
    )

    return update_dataset_config_operation
