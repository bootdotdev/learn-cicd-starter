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

"""Create command for Colab Enterprise Runtime Templates."""

from googlecloudsdk.api_lib.ai import operations
from googlecloudsdk.api_lib.colab_enterprise import runtime_templates as runtime_templates_util
from googlecloudsdk.api_lib.colab_enterprise import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.colab_enterprise import flags


_DETAILED_HELP = {
    'DESCRIPTION': """
        Create a Colab Enterprise runtime template, a VM configuration for your notebook runtimes.
    """,
    'EXAMPLES': """
        To create a runtime template in region 'us-central1' with the display name 'my-runtime-template', run:

        $ {command} --region=us-central1 --display-name=my-runtime-template

        To create a runtime template for a VM with machine type n1-standard-2 and one NVIDIA_TESLA_V100 accelerator, run:

        $ {command} --machine-type=n1-standard-2 --accelerator-type=NVIDIA_TESLA_V100 --accelerator-count=1 --region=us-central1 --display-name=my-runtime-template

        To create a runtime template that disables end user credential access, run:

        $ {command} --no-enable-euc --region=us-central1 --display-name=my-runtime-template
    """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA)
class Create(base.CreateCommand):
  """Create a runtime template."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.AddCreateRuntimeTemplateFlags(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command."""
    release_track = self.ReleaseTrack()
    messages = util.GetMessages(self.ReleaseTrack())
    region_ref = args.CONCEPTS.region.Parse()
    region = region_ref.AsDict()['locationsId']
    # Override to regionalize domain as used by the AIPlatform API.
    with endpoint_util.AiplatformEndpointOverrides(
        version='BETA', region=region
    ):
      api_client = util.GetClient(release_track)
      runtime_templates_service = (
          api_client.projects_locations_notebookRuntimeTemplates
      )
      operation = runtime_templates_service.Create(
          runtime_templates_util.CreateRuntimeTemplateCreateRequest(
              args, messages
          )
      )
      return util.WaitForOpMaybe(
          operations_client=operations.OperationsClient(client=api_client),
          op=operation,
          op_ref=runtime_templates_util.ParseRuntimeTemplateOperation(
              operation.name
          ),
          asynchronous=util.GetAsyncConfig(args),
          kind='runtime template',
          log_method='create',
          message='Waiting for runtime template to be created...',
      )


Create.detailed_help = _DETAILED_HELP
