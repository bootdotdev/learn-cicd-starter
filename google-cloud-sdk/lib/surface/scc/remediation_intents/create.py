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
"""Command for creating a Cloud Security Command Center RemediationIntent resource."""

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
class Create(base.CreateCommand):
  """Creates a remediation intent resource."""

  detailed_help = {
      "DESCRIPTION": """
        Create a Cloud Security Command Center (SCC)
        RemediationIntent resource.
        Created resource is returned as the response of the command.""",

      "EXAMPLES": """
          Sample usage:
          Create a manual workflow remediation intent resource:
          $ {{command}} scc remediation-intents create --parent=organizations/123456789/locations/global --finding-name=projects/123456789/sources/123456789/locations/global/findings/123456789 --workflow-type=manual

          Create a semi-autonomous workflow remediation intent resource:
          $ {{command}} scc remediation-intents create --parent=organizations/123456789/locations/global --workflow-type=semi-autonomous
          """,
  }

  @staticmethod
  def Args(parser):
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, False)
    flags.PARENT_NAME_FLAG.AddToParser(parser)
    flags.FINDING_NAME_FLAG.AddToParser(parser)
    flags.WORKFLOW_TYPE_FLAG.AddToParser(parser)
    parser.display_info.AddFormat("yaml")

  def Run(self, args):
    """The main function which is called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.
    Returns:
      Operation resource containing either resource or error.
    """
    client = sps_api.GetClientInstance(base.ReleaseTrack.ALPHA)
    messages = sps_api.GetMessagesModule(base.ReleaseTrack.ALPHA)

    # set workflow type based on the input argument value
    if args.workflow_type == "semi-autonomous":
      workflow_type = (
          messages.CreateRemediationIntentRequest.WorkflowTypeValueValuesEnum.WORKFLOW_TYPE_SEMI_AUTONOMOUS
      )
    elif args.workflow_type == "manual":
      workflow_type = (
          messages.CreateRemediationIntentRequest.WorkflowTypeValueValuesEnum.WORKFLOW_TYPE_MANUAL
      )
    else:
      workflow_type = (  # default value to be passed
          messages.CreateRemediationIntentRequest.WorkflowTypeValueValuesEnum.WORKFLOW_TYPE_UNSPECIFIED
      )

    # create the request object
    request = messages.SecuritypostureOrganizationsLocationsRemediationIntentsCreateRequest(
        parent=args.parent,
        createRemediationIntentRequest=messages.CreateRemediationIntentRequest(
            findingName=args.finding_name,
            workflowType=workflow_type,
        ),
    )
    # call the create remediation intent API
    operation = client.organizations_locations_remediationIntents.Create(
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
          message="Waiting for remediation intent to be created",
          has_result=True,
      )
