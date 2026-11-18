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
"""The update command for BigLake Iceberg REST catalogs."""

from googlecloudsdk.calliope import arg_parsers

from googlecloudsdk.api_lib.biglake import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.biglake import flags
from googlecloudsdk.core import log
from googlecloudsdk.core.util import times


@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Failover(base.Command):
  """Failover a BigLake Iceberg REST catalog."""

  @staticmethod
  def Args(parser):
    flags.AddCatalogResourceArg(parser, 'to failover')
    parser.add_argument(
        '--primary-replica',
        required=True,
        help='The primary replica region to failover to.',
    )
    parser.add_argument(
        '--validate-only',
        required=False,
        action='store_true',
        help='If true, the failover will be validated but not executed.',
    )
    parser.add_argument(
        '--conditional-failover-replication-time',
        required=False,
        type=arg_parsers.Datetime.ParseUtcTime,
        help=(
            'If not specified, wait for all data from the source region to'
            ' replicate to the new primary region before completing the'
            ' failover, with no data loss. If specified, the failover will be'
            ' executed immediately, accepting data loss of any data commited'
            ' after the specified timestamp. This timestamp must be in UTC'
            ' format, e.g. "2025-10-09T01:13:34.038262Z". See `$ gcloud topic'
            ' datetimes` for more information.'
        ),
    )

  def Run(self, args):
    client = util.GetClientInstance(self.ReleaseTrack())
    messages = client.MESSAGES_MODULE

    catalog_name = util.GetCatalogName(args.catalog)

    failover_request = messages.FailoverIcebergCatalogRequest(
        primaryReplica=args.primary_replica,
    )
    if args.IsSpecified('validate_only'):
      failover_request.validateOnly = args.validate_only
    if args.IsSpecified('conditional_failover_replication_time'):
      failover_request.conditionalFailoverReplicationTime = (
          times.FormatDateTime(args.conditional_failover_replication_time)
      )

    request = messages.BiglakeIcebergV1RestcatalogExtensionsProjectsCatalogsFailoverRequest(
        name=catalog_name,
        failoverIcebergCatalogRequest=failover_request,
    )
    response = (
        client.iceberg_v1_restcatalog_extensions_projects_catalogs.Failover(
            request
        )
    )
    if args.validate_only:
      log.UpdatedResource(
          catalog_name,
          details=f'Failover to [{args.primary_replica}] validated.',
      )
    else:
      log.UpdatedResource(
          catalog_name,
          details=f'Failover to [{args.primary_replica}] initiated.',
      )
    return response
