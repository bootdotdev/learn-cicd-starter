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
"""Lists supported model and server combinations for GKE Inference Quickstart."""

from googlecloudsdk.api_lib.ai.recommender import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import commands
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log

_EXAMPLES = """
To list all supported model and server combinations, run:

$ {command}
"""


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class List(commands.List):
  """List supported model and server combinations.

  This command lists all supported model, model server, and model server version
    combinations.
  """

  @staticmethod
  def Args(parser):
    parser.add_argument(
        "--model",
        help="The model. If not specified, this defaults to any model.",
    )
    parser.add_argument(
        "--model-server",
        help=(
            "The model server. If not specified, this defaults to any model"
            " server."
        ),
    )
    parser.add_argument(
        "--model-server-version",
        help=(
            "The model server version. If not specified, this defaults to the"
            " any model server version."
        ),
    )
    parser.display_info.AddFormat(
        "table(modelName, modelServerName, modelServerVersion)"
    )

  def Run(self, args):
    client = util.GetClientInstance(base.ReleaseTrack.ALPHA)
    messages = util.GetMessagesModule(base.ReleaseTrack.ALPHA)

    try:
      request = messages.GkerecommenderModelsAndServersListRequest(
          modelName=args.model,
          modelServerName=args.model_server,
          modelServerVersion=args.model_server_version,
      )
      response = client.modelsAndServers.List(request)
      if response.modelAndModelServerInfo:
        return response.modelAndModelServerInfo
      else:
        return []
    except exceptions.Error as e:
      log.error(f"An error has occurred: {e}")
      log.status.Print(f"An error has occurred: {e}")
      return []
