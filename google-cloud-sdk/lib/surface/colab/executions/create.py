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

"""Create command for Colab Enterprise Executions."""

from googlecloudsdk.api_lib.ai import operations
from googlecloudsdk.api_lib.colab_enterprise import util
from googlecloudsdk.api_lib.notebook_executor import executions as executions_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.notebook_executor import flags


_DETAILED_HELP = {
    'DESCRIPTION': """
        Create a notebook execution to be used on a Colab Enterprise runtime.
    """,
    'EXAMPLES': """
        To create an execution of a notebook file with Cloud Storage URI `gs://my-bucket/my-notebook.ipynb`, with an execution job display name `my-execution`, compute configured from runtime template `my-runtime-template-id`, running with service account `my-service-account@my-project.iam.gserviceaccount.com`, with results uploaded to Cloud Storage bucket `gs://my-bucket/results`, and in region `us-central1` run:

         $ {command} --display-name=my-execution --runtime-template=my-runtime-template-id --gcs-notebook-uri=gs://my-bucket/my-notebook.ipynb --service-account=my-service-account@my-project.iam.gserviceaccount.com --gcs-output-uri=gs://my-bucket/results --region=us-central1
    """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA)
class Create(base.CreateCommand):
  """Create an execution."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.AddCreateExecutionFlags(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command."""
    release_track = self.ReleaseTrack()
    messages = util.GetMessages(self.ReleaseTrack())
    region_ref = args.CONCEPTS.region.Parse()
    region = region_ref.AsDict()['locationsId']
    with endpoint_util.AiplatformEndpointOverrides(
        version='BETA', region=region
    ):
      api_client = util.GetClient(release_track)
      executions_service = (
          api_client.projects_locations_notebookExecutionJobs
      )
      operation = executions_service.Create(
          executions_util.CreateExecutionCreateRequest(
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
          log_method='create',
          message='Waiting for execution to be created...',
      )


Create.detailed_help = _DETAILED_HELP
