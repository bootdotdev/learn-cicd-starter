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

"""Update command for Colab Enterprise Schedules."""

from googlecloudsdk.api_lib.colab_enterprise import util
from googlecloudsdk.api_lib.notebook_executor import schedules as schedules_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.notebook_executor import flags
from googlecloudsdk.core import log

_DETAILED_HELP = {
    'DESCRIPTION': """
        Update a Colab Enterprise notebook execution schedule.
    """,
    'EXAMPLES': """
        To update the cron schedule and max runs of a schedule with id `my-schedule`, in region `us-central1`, run:

        $ {command} my-schedule --region=us-central1 --cron-schedule='TZ=America/Los_Angeles 0 0 * * 0' --max-runs=2
    """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA)
class Update(base.UpdateCommand):
  """Update a schedule."""

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: argparse parser for the command
    """
    flags.AddCreateOrUpdateScheduleFlags(parser, is_update=True)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      The API response for updating the schedule.
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
      # Although API will error if schedule is not of notebook execution type,
      # validate client-side for better ux / consistency with other commands.
      schedules_util.ValidateAndGetColabSchedule(
          args, messages, schedules_service
      )
      schedule = schedules_service.Patch(
          schedules_util.CreateSchedulePatchRequest(args, messages)
      )
      log.UpdatedResource(resource=schedule.name, kind='schedule')
      return schedule

Update.detailed_help = _DETAILED_HELP
