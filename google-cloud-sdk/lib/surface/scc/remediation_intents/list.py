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
"""Command for listing a Cloud Security Command Center RemediationIntent resources."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from apitools.base.py import list_pager
from googlecloudsdk.api_lib.scc.remediation_intents import sps_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scc.remediation_intents import flags


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class List(base.ListCommand):
  """Lists the remediation intent resources."""

  detailed_help = {
      "DESCRIPTION": """
        Lists the Cloud Security Command Center (SCC)
        RemediationIntent resources.
        List of resources is returned as the response of the command.""",

      "EXAMPLES": """
          Sample usage:
          List all remediation intent resource under parent organizations/123456789/locations/global:
          $ {{command}} scc remediation-intents list organizations/123456789/locations/global
          """,
  }

  @staticmethod
  def Args(parser):
    flags.POSITIONAL_PARENT_NAME_FLAG.AddToParser(parser)
    parser.display_info.AddFormat("table(name)")

  def Run(self, args):
    """The main function which is called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.
    Returns:
      List of remediation intent resources as per the request.
    """
    client = sps_api.GetClientInstance(base.ReleaseTrack.ALPHA)
    messages = sps_api.GetMessagesModule(base.ReleaseTrack.ALPHA)

    # create the request object
    request = messages.SecuritypostureOrganizationsLocationsRemediationIntentsListRequest(
        parent=args.parent,
        filter=args.filter,
    )

    return list_pager.YieldFromList(
        client.organizations_locations_remediationIntents,
        request,
        field="remediationIntents",
        limit=args.limit,
        batch_size_attribute="pageSize")
