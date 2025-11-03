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
"""List protection summary."""


from googlecloudsdk.api_lib.backupdr import rbc_filter_rewrite
from googlecloudsdk.api_lib.backupdr import resource_backup_config
from googlecloudsdk.api_lib.util import common_args
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.core import log
from googlecloudsdk.core.resource import resource_projection_spec


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class List(base.ListCommand):
  """Show backup configuration metadata associated with specified resources in a particular location for the project."""
  detailed_help = {
      'BRIEF': (
          'list backup configurations for a specified project and location.'
      ),
      'DESCRIPTION': (
          '{description}'
      ),
      'FLAGS/ARGUMENTS': """\
          `--project`: Project for which backup configurations should be listed.

          `--location`: Location for which backup configurations should be listed.

          `--filter`: The filter expression to filter results.

          `--sort-by`: The field to sort results by.
          """,
      'SUBARGUMENTS': """\
          `target_resource_display_name`: Name of the resource for which protection summary is to be listed.

          `target_resource_type`: Type of resource for which protection summary is to be displayed.\n
          Allowed values:
              * CLOUD_SQL_INSTANCE
              * COMPUTE_ENGINE_VM

          `backup_configured`: Displays if the specified resource has backups configured.

          `vaulted`: Displays if configured backups are protected using a backup vault.

          `backup_configs_details.backup_config_source_display_name`: Name of the backup schedule applied to the resource.

          `backup_configs_details.type`: Backup schedule type applied to the resource.\n
          Allowed values:
              * CLOUD_SQL_INSTANCE_BACKUP_CONFIG
              * COMPUTE_ENGINE_RESOURCE_POLICY
              * BACKUPDR_BACKUP_PLAN
              * BACKUPDR_TEMPLATE
          """,
      'EXAMPLES': """\
          * To list protection summary for a resource named `resource-1`:

              $ {command} --project=sample-project --location=us-central1 --filter="target_resource_display_name=resource-1"

          * To list protection summary for a resource named `resource-1` that has backup configured:

              $ {command} --project=sample-project --location=us-central1 --filter="target_resource_display_name=resource-1 AND backup_configured=true"

        You can sort the results using the `--sort-by` flag. The only supported field for sorting is `target_resource_display_name`.

        Example of sorting:

          $ {command} --project=sample-project --location=us-central1 --sort-by="target_resource_display_name"
        """,
  }

  @staticmethod
  def Args(parser):
    flags.AddLocationResourceArg(
        parser,
        'Location for which the resource backup config should be listed.',
    )

  def _Validate_and_Parse_SortBy(self, args):
    order_by = common_args.ParseSortByArg(args.sort_by)
    # Only sort by target_resource_display_name is supported by CLH right now.
    if order_by is None:
      return None
    order_by_fields = order_by.split(' ')
    if (
        order_by_fields
        and isinstance(order_by_fields[0], str)
        and order_by_fields[0]
        not in ('target_resource_display_name', 'targetResourceDisplayName')
    ):
      raise exceptions.InvalidArgumentException(
          'sort_by',
          'Invalid sort_by argument. Only sort_by'
          ' target_resource_display_name/targetResourceDisplayName is'
          ' supported.',
      )
    order_by_fields[0] = 'target_resource_display_name'
    order_by = ' '.join(order_by_fields)
    return order_by

  def Run(self, args):
    """Constructs and sends request."""
    # Location is required.
    if args.location is None:
      raise exceptions.RequiredArgumentException(
          'location',
          'Location for which the resource backup config should be listed.',
      )

    client = resource_backup_config.ResourceBackupConfigClient()
    parent_ref = args.CONCEPTS.location.Parse()

    # Client and server side filtering.
    display_info = args.GetDisplayInfo()
    defaults = resource_projection_spec.ProjectionSpec(
        symbols=display_info.transforms, aliases=display_info.aliases
    )

    _, server_filter = rbc_filter_rewrite.ListFilterRewrite().Rewrite(
        args.filter, defaults=defaults)
    log.info('original_filter=%r, server_filter=%r',
             args.filter, server_filter)

    # No client side filtering.
    args.filter = None
    if args.page_size is not None:
      # Server side limit.
      args.page_size = min(500, args.page_size)

    if not args.format:
      args.format = 'json'
    order_by = self._Validate_and_Parse_SortBy(args)

    return client.List(
        parent=parent_ref.RelativeName(),
        filters=server_filter,
        page_size=args.page_size,
        limit=args.limit,
        order_by=order_by,
    )
