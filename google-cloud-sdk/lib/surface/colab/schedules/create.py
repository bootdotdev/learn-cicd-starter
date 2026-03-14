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

"""Create command for Colab Enterprise Schedules."""

from googlecloudsdk.api_lib.colab_enterprise import util
from googlecloudsdk.api_lib.notebook_executor import schedules as schedules_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.notebook_executor import flags
from googlecloudsdk.core import log

_DETAILED_HELP = {
    'DESCRIPTION': """
        Create a schedule to run a Colab Enterprise notebook execution job.
    """,
    'EXAMPLES': """
      To create a schedule in region `us-central1` with the following schedule properties:
        - display name: `my-schedule`,
        - cron schedule: `TZ=America/Los_Angeles * * * * *`,
        - maximum concurrent runs allowed: 1,
        - start time: 2025-01-01T00:00:00-06:00,

      for a notebook execution job:
        - with display name `my-execution`,
        - running notebook file from Cloud Storage URI `gs://my-bucket/my-notebook.ipynb`,
        - compute configured from runtime template `my-runtime-template-id`,
        - running with service account `my-service-account@my-project.iam.gserviceaccount.com`,
        - with results uploaded to Cloud Storage bucket `gs://my-bucket/results`

      Run the following command:
        $ {command} --region=us-central1 --display-name=my-schedule --cron-schedule='TZ=America/Los_Angeles * * * * *' --max-concurrent-runs=1 --start-time=2025-01-01T00:00:00-06:00 --execution-display-name=my-execution --notebook-runtime-template=my-runtime-template-id --gcs-notebook-uri=gs://my-bucket/my-notebook.ipynb --service-account=my-service-account@my-project.iam.gserviceaccount.com --gcs-output-uri=gs://my-bucket/results
    """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA)
class Create(base.CreateCommand):
  """Create a schedule."""

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: argparse parser for the command
    """
    flags.AddCreateOrUpdateScheduleFlags(parser, is_update=False)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      The API response for creating the schedule.
    """
    release_track = self.ReleaseTrack()
    messages = util.GetMessages(self.ReleaseTrack())
    region_ref = args.CONCEPTS.region.Parse()
    region = region_ref.AsDict()['locationsId']
    with endpoint_util.AiplatformEndpointOverrides(
        version='BETA', region=region
    ):
      api_client = util.GetClient(release_track)
      schedules_service = api_client.projects_locations_schedules
      schedule = schedules_service.Create(
          schedules_util.CreateScheduleCreateRequest(args, messages)
      )
      log.CreatedResource(resource=schedule.name, kind='schedule')
      return schedule


Create.detailed_help = _DETAILED_HELP
