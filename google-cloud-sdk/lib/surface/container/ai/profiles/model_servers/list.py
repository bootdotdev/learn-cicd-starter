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
"""Lists supported model servers for GKE Inference Quickstart."""

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.ai.recommender import util
from googlecloudsdk.api_lib.util import exceptions as api_lib_exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import commands
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log


_EXAMPLE = """
To list all supported model servers for a model, run:

$ {command} --model=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
"""


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class List(commands.List):
  """List supported model servers for a given model.

  To get supported models, run `gcloud container ai profiles models
  list`.
  """

  @staticmethod
  def Args(parser):
    parser.add_argument(
        "--model",
        required=True,
        help="The model.",
    )

  def Run(self, args):
    client = util.GetClientInstance(base.ReleaseTrack.GA)
    messages = util.GetMessagesModule(base.ReleaseTrack.GA)

    try:
      request = messages.GkerecommenderModelServersFetchRequest(
          model=args.model
      )
      response = client.modelServers.Fetch(request)
      if response.modelServers:
        return response.modelServers
      else:
        return []
    except apitools_exceptions.HttpError as error:
      raise api_lib_exceptions.HttpException(error, util.HTTP_ERROR_FORMAT)

  def Display(self, _, resources):
    if resources:
      log.out.Print("Supported model servers:")
      for model_server_name in resources:
        log.out.Print("- ", model_server_name)
    else:
      log.out.Print("No supported model servers found.")


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ListAlpha(commands.List):
  """List supported model servers for a given model.

  To get supported models, run `gcloud alpha container ai profiles models
  list` or to get all supported model and server combinations, run `gcloud alpha
  container ai profiles model-and-server-combinations
  list`.
  """

  @staticmethod
  def Args(parser):
    parser.add_argument(
        "--model",
        required=True,
        help="The model.",
    )

  def Run(self, args):
    client = util.GetClientInstance(base.ReleaseTrack.ALPHA)
    messages = util.GetMessagesModule(base.ReleaseTrack.ALPHA)

    try:
      request = messages.GkerecommenderModelServersListRequest(
          modelName=args.model
      )
      response = client.modelServers.List(request)
      if response.modelServerNames:
        return response.modelServerNames
      else:
        return []
    except exceptions.Error as e:
      log.error(f"An error has occurred: {e}")
      log.status.Print(f"An error has occurred: {e}")
      return []

  def Display(self, _, resources):
    if resources:
      log.out.Print("Supported model servers:")
      for model_server_name in resources:
        log.out.Print("- ", model_server_name)
    else:
      log.out.Print("No supported model servers found.")
