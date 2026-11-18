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

"""Upgrade command for Colab Enterprise Runtimes."""

from googlecloudsdk.api_lib.ai import operations
from googlecloudsdk.api_lib.colab_enterprise import runtimes as runtimes_util
from googlecloudsdk.api_lib.colab_enterprise import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.colab_enterprise import flags


_DETAILED_HELP = {
    'DESCRIPTION': """
        Upgrade a Colab Enterprise notebook runtime.
    """,
    'EXAMPLES': """
        To upgrade a runtime with id 'my-runtime' in region 'us-central1', run:

        $ {command} my-runtime --region=us-central1
    """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA)
class Upgrade(base.UpdateCommand):
  """Upgrade a runtime."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.AddUpgradeRuntimeFlags(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command."""
    release_track = self.ReleaseTrack()
    messages = util.GetMessages(self.ReleaseTrack())
    runtime_ref = args.CONCEPTS.runtime.Parse()
    region = runtime_ref.AsDict()['locationsId']
    # Override to regionalize domain as used by the AIPlatform API.
    with endpoint_util.AiplatformEndpointOverrides(
        version='BETA', region=region
    ):
      api_client = util.GetClient(release_track)
      runtime_service = (
          api_client.projects_locations_notebookRuntimes
      )
      operation = runtime_service.Upgrade(
          runtimes_util.CreateRuntimeUpgradeRequestMessage(args, messages)
      )
      return util.WaitForOpMaybe(
          operations_client=operations.OperationsClient(client=api_client),
          op=operation,
          op_ref=runtimes_util.ParseRuntimeOperation(
              operation.name
          ),
          log_method='update',
          kind='runtime',
          asynchronous=util.GetAsyncConfig(args),
          message='Upgrading runtime...',
          resource=args.CONCEPTS.runtime.Parse().RelativeName(),
      )


Upgrade.detailed_help = _DETAILED_HELP
