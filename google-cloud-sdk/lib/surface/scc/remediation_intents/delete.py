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
"""Command for deleting a Cloud Security Command Center RemediationIntent resource."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from googlecloudsdk.api_lib.scc.remediation_intents import sps_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scc.remediation_intents import flags
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class Delete(base.DeleteCommand):
  """Deletes a remediation intent resource."""

  detailed_help = {
      "DESCRIPTION": """
        Deletes a Cloud Security Command Center (SCC)
        RemediationIntent resource.""",

      "EXAMPLES": """
          Sample usage:
          Delete a remediation intent resource of name organizations/123456789/locations/global/remediationIntents/123:
          $ {{command}} scc remediation-intents delete organizations/123456789/locations/global/remediationIntents/123
          """,
  }

  @staticmethod
  def Args(parser):
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, False)
    flags.ETAG_FLAG.AddToParser(parser)
    flags.AddRemediationIntentResourceArg(parser)

  def Run(self, args):
    """The main function which is called when the user runs this command.

    Args:
      args: An argparse namespace. All the arguments that were provided to this
        command invocation.
    Returns:
      Operation resource containing success or error.
    """
    client = sps_api.GetClientInstance(base.ReleaseTrack.ALPHA)
    messages = sps_api.GetMessagesModule(base.ReleaseTrack.ALPHA)

    # parse the remediation intent resource argument
    ri_ref = args.CONCEPTS.remediationintent.Parse()
    ri_name = ri_ref.RelativeName()
    # create the request object
    request = messages.SecuritypostureOrganizationsLocationsRemediationIntentsDeleteRequest(
        name=ri_name,
        etag=args.etag,
    )
    # call the create remediation intent API
    operation = client.organizations_locations_remediationIntents.Delete(
        request=request
    )
    operation_id = operation.name

    if args.async_:   # Return the in-progress operation if async is requested.
      log.status.Print(
          "Check for operation completion status using operation ID:",
          operation_id,
      )
      return operation
    else:   # Poll the operation until it completes and return resource
      return sps_api.WaitForOperation(
          operation_ref=sps_api.GetOperationsRef(operation_id),
          message="Waiting for remediation intent to be deleted",
          has_result=False,
      )
