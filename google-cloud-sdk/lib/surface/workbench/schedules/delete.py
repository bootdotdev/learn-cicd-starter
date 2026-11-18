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

"""Delete command for Workbench Schedules."""

from googlecloudsdk.api_lib.ai import operations
from googlecloudsdk.api_lib.colab_enterprise import util
from googlecloudsdk.api_lib.notebook_executor import schedules as schedules_util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import parser_arguments
from googlecloudsdk.calliope import parser_extensions
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.notebook_executor import flags


_DETAILED_HELP = {
    'DESCRIPTION': """
        Delete a Workbench notebook execution schedule.
    """,
    'EXAMPLES': """
        To delete a schedule with id `my-schedule`, in region `us-central1`, run:

         $ {command} my-schedule --region=us-central1
    """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class Delete(base.DeleteCommand):
  """Delete a schedule."""

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor):
    """Register flags for this command.

    Args:
      parser: argparse parser for the command.
    """
    flags.AddDeleteScheduleFlags(parser)

  def Run(self, args: parser_extensions.Namespace):
    """This is what gets called when the user runs this command.

    Args:
      args: the arguments that this command was invoked with.

    Returns:
      The response from the API.
    """
    release_track = self.ReleaseTrack()
    messages = util.GetMessages(self.ReleaseTrack())
    schedule_ref = args.CONCEPTS.schedule.Parse()
    region = schedule_ref.AsDict()['locationsId']
    with endpoint_util.AiplatformEndpointOverrides(
        version='BETA', region=region
    ):
      api_client = util.GetClient(release_track)
      schedules_service = (
          api_client.projects_locations_schedules
      )
      # We skip validating the schedule type for deletion as a workaround to
      # allow the gcloud e2e script to delete both Colab Enterprise and
      # Workbench schedules. Currently the e2e script does not allow specifying
      # multiple commands for deleting a single API resource.
      schedules_util.ValidateAndGetWorkbenchSchedule(
          args, messages, schedules_service, skip_workbench_check=True
      )
      operation = schedules_service.Delete(
          schedules_util.CreateScheduleDeleteRequest(
              args, messages
          )
      )
      return util.WaitForOpMaybe(
          operations_client=operations.OperationsClient(client=api_client),
          op=operation,
          op_ref=schedules_util.ParseScheduleOperation(
              operation.name
          ),
          asynchronous=util.GetAsyncConfig(args),
          kind='schedule',
          log_method='delete',
          message='Waiting for schedule to be deleted...',
      )


Delete.detailed_help = _DETAILED_HELP
