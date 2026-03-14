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
"""Command for updating a Cloud Security Command Center RemediationIntent resource."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from apitools.base.py import encoding
from googlecloudsdk.api_lib.scc.remediation_intents import sps_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scc.remediation_intents import flags
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class Update(base.UpdateCommand):
  """Updates a remediation intent resource."""

  detailed_help = {
      "DESCRIPTION": """
        Updates a Cloud Security Command Center (SCC)
        RemediationIntent resource.\n
        Fields specified in update-mask flag are updated. Updatable fields depends on the state transition.\n
        Valid state transitions are:\n
        a) ENQUEUED to IN_PROGRESS (mask: state,remediation_input)\n
        b) REMEDIATION_SUCCESS to PR_GENERATION_SUCCESS (mask: state,remediation_artifacts)\n
        c) REMEDIATION_SUCCESS to PR_GENERATION_FAILED (mask: state,error_details)\n
        An empty or * as field mask will result in updating the relevant fields as per the transition.\n
        Updated resource is returned as the response of the command.""",

      "EXAMPLES": """
          Sample usage:
          Update the remediation intent resource's state from ENQUEUED to IN_PROGRESS:
          $ {{command}} scc remediation-intents update organizations/123456789/locations/global/remediationIntents/123456789 --ri-from-file=/path/to/resource.yaml --update-mask=state,remediation_input
          \n
          Update the remediation intent resource's state from ENQUEUED to IN_PROGRESS (with empty update mask):
          $ {{command}} scc remediation-intents update organizations/123456789/locations/global/remediationIntents/123456789 --ri-from-file=/path/to/resource.yaml
          \n
          Update the remediation intent resource's state from REMEDIATION_SUCCESS to PR_GENERATION_SUCCESS:
          $ {{command}} scc remediation-intents update organizations/123456789/locations/global/remediationIntents/123456789 --ri-from-file=/path/to/resource.yaml --update-mask=state,remediation_artifacts
          \n
          Update the remediation intent resource's state from REMEDIATION_SUCCESS to PR_GENERATION_FAILED:
          $ {{command}} scc remediation-intents update organizations/123456789/locations/global/remediationIntents/123456789 --ri-from-file=/path/to/resource.yaml --update-mask=state,error_details
          """,
  }

  @staticmethod
  def Args(parser):
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, False)
    flags.AddRemediationIntentResourceArg(parser)
    flags.REMEDIATION_INTENT_FROM_FILE_FLAG.AddToParser(parser)
    flags.UPDATE_MASK_FLAG.AddToParser(parser)
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

    # Set mask based on the input argument value.
    if args.update_mask is None:
      update_mask = "*"   # update all relevant fields
    else:
      update_mask = args.update_mask

    # parse the remediation intent resource argument
    ri_ref = args.CONCEPTS.remediationintent.Parse()
    ri_name = ri_ref.RelativeName()

    # create the request object
    request = messages.SecuritypostureOrganizationsLocationsRemediationIntentsPatchRequest(
        name=ri_name,
        remediationIntent=encoding.DictToMessage(
            args.ri_from_file,  # dict object containing the resource
            messages.RemediationIntent,
        ),
        updateMask=update_mask,
    )

    # call the update remediation intent API
    operation = client.organizations_locations_remediationIntents.Patch(
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
          message="Waiting for remediation intent to be updated",
          has_result=True,
      )
