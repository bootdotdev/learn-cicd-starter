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
          Create an insights config.
          """,
    'EXAMPLES': """
          To create an insights config, run:

            $ {command} insights-config-name --app-hub-application=projects/my-project/locations/us-central1/applications/my-app-hub-application
          """,
}


@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
@base.DefaultUniverseOnly
class Create(base.CreateCommand):
  """Create an insight config."""

  @staticmethod
  def Args(parser):
    """Adds arguments for this command."""
    try:
      resource_args.AddInsightConfigResourceArg(parser, verb='create')
    except exceptions.HttpException as e:
      log.status.Print('Failed to add insight config resource argument.')
      raise e

    # Relevant argument.
    flags.AddAppHubApplicationArgument(parser)
    flags.AddArtifactConfigsArgument(parser)

  def Run(self, args):
    max_wait = datetime.timedelta(seconds=30)
    client = insights_config.InsightsConfigClient(base.ReleaseTrack.ALPHA)
    insights_config_ref = args.CONCEPTS.insights_config.Parse()
    try:
      operation = client.Create(
          insight_config_ref=insights_config_ref,
          app_hub=args.app_hub_application,
          user_artifact_configs=args.artifact_configs,
      )
    except exceptions.HttpException as e:
      log.status.Print('Failed to create the insight config {}.'.format(
          insights_config_ref.RelativeName()
      ))
      raise e

    log.status.Print('Creating the insight config {}.'.format(
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
Create.detailed_help = DETAILED_HELP
