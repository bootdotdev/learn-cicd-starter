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
"""Lists supported model server versions for GKE Inference Quickstart."""

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.ai.recommender import util
from googlecloudsdk.api_lib.util import exceptions as api_lib_exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import commands
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log


_EXAMPLES = """
To list all supported model server versions for a model and model server, run:

$ {command} --model=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --model-server=vllm
"""


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class List(commands.List):
  """List supported model server versions.

  To get supported model and model servers, run `gcloud container ai
  profiles models list` and `gcloud container ai profiles
  model-servers list`.
  """

  @staticmethod
  def Args(parser):
    parser.add_argument(
        "--model",
        required=True,
        help="The model.",
    )
    parser.add_argument(
        "--model-server",
        required=True,
        help=(
            "The model server. If not specified, this defaults to any model"
            " server."
        ),
    )

  def Run(self, args):
    client = util.GetClientInstance(base.ReleaseTrack.GA)
    messages = util.GetMessagesModule(base.ReleaseTrack.GA)

    try:
      request = messages.GkerecommenderModelServerVersionsFetchRequest(
          model=args.model, modelServer=args.model_server
      )
      response = client.modelServerVersions.Fetch(request)
      if response.modelServerVersions:
        return response.modelServerVersions
      else:
        return []
    except apitools_exceptions.HttpError as error:
      raise api_lib_exceptions.HttpException(error, util.HTTP_ERROR_FORMAT)

  def Display(self, _, resources):
    if resources:
      log.out.Print("Supported model server versions:")
      for model_server_version in resources:
        log.out.Print("- ", model_server_version)
    else:
      log.out.Print("No supported model server versions found.")


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ListAlpha(commands.List):
  """List supported model server versions.

  To get supported model and model servers, run `gcloud alpha container ai
  profiles models list` and `gcloud alpha container ai profiles
  model-servers list`.
  Alternatively, run `gcloud alpha container ai profiles
  model-and-server-combinations list` to get all supported model and server
  combinations.
  """

  @staticmethod
  def Args(parser):
    parser.add_argument(
        "--model",
        required=True,
        help="The model.",
    )
    parser.add_argument(
        "--model-server",
        required=True,
        help=(
            "The model server. If not specified, this defaults to any model"
            " server."
        ),
    )

  def Run(self, args):
    client = util.GetClientInstance(base.ReleaseTrack.ALPHA)
    messages = util.GetMessagesModule(base.ReleaseTrack.ALPHA)

    try:
      request = messages.GkerecommenderModelServersVersionsListRequest(
          modelName=args.model, modelServerName=args.model_server
      )
      response = client.modelServers_versions.List(request)
      if response.modelServerVersions:
        return response.modelServerVersions
      else:
        return []
    except exceptions.Error as e:
      log.error(f"An error has occurred: {e}")
      log.status.Print(f"An error has occurred: {e}")
      return []

  def Display(self, _, resources):
    if resources:
      log.out.Print("Supported model server versions:")
      for model_server_version in resources:
        log.out.Print("- ", model_server_version)
    else:
      log.out.Print("No supported model server versions found.")
