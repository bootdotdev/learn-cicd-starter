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
"""Update the configuration of an insight config."""

import datetime

from googlecloudsdk.api_lib.developer_connect.insights_configs import insights_config
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.developer_connect import flags
from googlecloudsdk.command_lib.developer_connect import resource_args
from googlecloudsdk.core import log

DETAILED_HELP = {
    'DESCRIPTION': """
          Update the configuration of an insights config.
          """,
    'EXAMPLES': """
          To update the state of an insights config, run:

            $ {command} insights-config-name --run-discovery

          To update the Artifact Analysis project for an artifact in an insights config, run:

            $ {command} insights-config-name --artifact-uri=us-{location}-docker.pkg.dev/my-project/my-artifact-repo/my-image --build-project={build_project}
          """,
}


@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
@base.DefaultUniverseOnly
class Update(base.UpdateCommand):
  """Update the configuration of an insight config."""

  @staticmethod
  def Args(parser):
    """Adds arguments for this command."""
    try:
      resource_args.AddInsightConfigResourceArg(parser, verb='update')
    except exceptions.HttpException as e:
      log.status.Print('Failed to add insight config resource argument.')
      raise e

    # Relevant arguments and groups.
    update_group = parser.add_group(
        required=True, help='Update the insight config.'
    )
    artifact_group = update_group.add_group()
    flags.AddDiscoveryArgument(update_group)
    flags.AddArtifactArgument(artifact_group)
    flags.AddBuildProjectArgument(artifact_group)

  def Run(self, args):
    max_wait = datetime.timedelta(seconds=30)
    client = insights_config.InsightsConfigClient(base.ReleaseTrack.ALPHA)
    insights_config_ref = args.CONCEPTS.insights_config.Parse()
    try:
      operation = client.Update(
          insight_config_ref=insights_config_ref,
          discovery=args.run_discovery,
          build_project=args.build_project,
          artifact_uri=args.artifact_uri,
      )
    except exceptions.HttpException as e:
      log.status.Print('Failed to update the insight config {}.'.format(
          insights_config_ref.RelativeName()
      ))
      raise e

    log.status.Print('Updating the insight config {}.'.format(
        insights_config_ref.RelativeName()
    ))

    return client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message='Waiting for operation [{}] to be completed...'
        .format(
            client.GetOperationRef(operation).RelativeName()),
        has_result=True,
        max_wait=max_wait,
    )
Update.detailed_help = DETAILED_HELP
