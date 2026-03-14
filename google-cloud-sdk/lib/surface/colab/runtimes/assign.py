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

"""Assign command for Colab Enterprise Runtimes."""

from googlecloudsdk.api_lib.ai import operations
from googlecloudsdk.api_lib.colab_enterprise import runtimes as runtimes_util
from googlecloudsdk.api_lib.colab_enterprise import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.colab_enterprise import flags


_DETAILED_HELP = {
    'DESCRIPTION': """
        Assign a notebook runtime to run code from your notebook (IPYNB file).
    """,
    'EXAMPLES': """
        To create a runtime in region 'us-central1' with the display name 'my-runtime' and template with id 'my-template', run:

        $ {command} --region=us-central1 --display-name=my-runtime --runtime-template=my-template

        To create a runtime for user 'USER@DOMAIN.COM', run:

        $ {command} --runtime-user=USER@DOMAIN.COM --region=us-central1 --display-name=my-runtime --runtime-template=my-template
    """,
}


@base.Deprecate(
    is_removed=True,
    warning=(
        'This command is deprecated. '
        'Please use `gcloud beta colab runtimes create` instead.'
    ),
    error=(
        'This command has been removed. '
        'Please use `gcloud beta colab runtimes create` instead.'
    ),
)
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class Create(base.CreateCommand):
  """Assign a notebook runtime."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.AddCreateRuntimeFlags(parser)

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
      runtimes_service = api_client.projects_locations_notebookRuntimes
      operation = runtimes_service.Assign(
          runtimes_util.CreateRuntimeAssignRequestMessage(args, messages)
      )
      return util.WaitForOpMaybe(
          operations_client=operations.OperationsClient(client=api_client),
          op=operation,
          op_ref=runtimes_util.ParseRuntimeOperation(operation.name),
          asynchronous=util.GetAsyncConfig(args),
          kind='runtime',
          log_method='create',
          message=(
              'Assigning a runtime to'
              f' {runtimes_util.GetRuntimeUserFromArgsOrProperties(args)}...'
          ),
      )


Create.detailed_help = _DETAILED_HELP
