# -*- coding: utf-8 -*- #
# Copyright 2024 Google LLC. All Rights Reserved.
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

"""Delete command for Workbench Executions."""

from googlecloudsdk.api_lib.ai import operations
from googlecloudsdk.api_lib.colab_enterprise import util
from googlecloudsdk.api_lib.notebook_executor import executions as executions_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.notebook_executor import flags


_DETAILED_HELP = {
    'DESCRIPTION': """
        Delete a Workbench notebook execution.
    """,
    'EXAMPLES': """
        To delete an execution with id `my-execution`, in region `us-central1`, run:

         $ {command} my-execution --region=us-central1
    """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class Delete(base.DeleteCommand):
  """Delete an execution."""

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: argparse parser for the command.
    """
    flags.AddDeleteExecutionFlags(parser, for_workbench=True)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: argparse namespace, the arguments of the command.

    Returns:
      The delete operation or the results if async.
    """
    release_track = self.ReleaseTrack()
    messages = util.GetMessages(self.ReleaseTrack())
    execution_ref = args.CONCEPTS.execution.Parse()
    region = execution_ref.locationsId
    with endpoint_util.AiplatformEndpointOverrides(
        version='BETA', region=region
    ):
      api_client = util.GetClient(release_track)
      executions_service = (
          api_client.projects_locations_notebookExecutionJobs
      )
      # We skip validating the execution type for deletion as a workaround to
      # allow the gcloud e2e script to delete both Colab Enterprise and
      # Workbench executions. Currently the e2e script does not allow specifying
      # multiple commands for deleting a single API resource.
      executions_util.ValidateAndGetWorkbenchExecution(
          args, messages, executions_service, skip_workbench_check=True
      )
      operation = executions_service.Delete(
          executions_util.CreateExecutionDeleteRequest(
              args, messages
          )
      )
      return util.WaitForOpMaybe(
          operations_client=operations.OperationsClient(client=api_client),
          op=operation,
          op_ref=executions_util.ParseExecutionOperation(
              operation.name
          ),
          asynchronous=util.GetAsyncConfig(args),
          kind='notebook execution',
          log_method='delete',
          message='Waiting for execution to be deleted...',
      )


Delete.detailed_help = _DETAILED_HELP
