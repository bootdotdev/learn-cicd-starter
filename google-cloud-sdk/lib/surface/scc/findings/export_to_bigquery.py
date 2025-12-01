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
"""Command to export Security Command Center findings to bigquery."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from googlecloudsdk.api_lib.scc import securitycenter_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scc import flags as scc_flags
from googlecloudsdk.command_lib.scc.findings import flags
from googlecloudsdk.command_lib.scc.findings import util


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Export(base.Command):
  """Export Security Command Center findings to bigquery."""

  detailed_help = {
      "DESCRIPTION": "Export Security Command Center findings to bigquery.",
      "EXAMPLES": """
      To export findings for a given parent ``organizations/123/sources/456/locations/global`` and dataset ``projects/project_id/datasets/dataset_id`` run:

        $ {command} organizations/123 --dataset=projects/project_id/datasets/dataset_id --source=456 --location=global

      """,
      "API REFERENCE": (
          """
      This command uses the Security Command Center API. For more information,
      see [Security Command Center API.](https://cloud.google.com/security-command-center/docs/reference/rest)"""
      ),
  }

  @staticmethod
  def Args(parser):

    scc_flags.AppendParentArg()[0].AddToParser(parser)
    flags.SOURCE_FLAG.AddToParser(parser)
    scc_flags.LOCATION_FLAG.AddToParser(parser)

    parser.add_argument(
        "--dataset",
        help="BigQuery dataset to export findings to.",
        required=True,
    )

  def Run(self, args):
    version = "v2"
    messages = securitycenter_client.GetMessages(version)
    client = securitycenter_client.GetClient(version)

    if args.parent is None:
      raise ValueError("Parent must be specified.")

    request = (
        messages.SecuritycenterOrganizationsSourcesLocationsFindingsExportRequest()
    )

    validated_dataset = util.ValidateDataset(args.dataset)
    request.exportFindingsRequest = messages.ExportFindingsRequest(
        bigQueryDestination=messages.BigQueryDestination(
            dataset=validated_dataset
        ),
    )
    request.parent = _GenerateParentResource(args, version)
    return client.organizations_sources_locations_findings.Export(request)


def _GenerateParentResource(args, version="v2"):
  """Generate a parent's name and parent using org, source and finding id."""
  util.ValidateMutexOnSourceAndParent(args)

  if args.parent and "/sources/" in args.parent:
    args.source = args.parent

  parent = util.GetFullSourceName(args, version)
  return parent
