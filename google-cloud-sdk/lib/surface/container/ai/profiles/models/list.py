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
"""Lists supported models for GKE Inference Quickstart."""

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.ai.recommender import util
from googlecloudsdk.api_lib.util import exceptions as api_lib_exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import commands
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log


_EXAMPLES = """
To list all supported models, run:

$ {command}
"""


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class List(commands.List):
  """List supported models."""

  def Run(self, _):
    client = util.GetClientInstance(base.ReleaseTrack.GA)
    messages = util.GetMessagesModule(base.ReleaseTrack.GA)

    try:
      response = client.models.Fetch(
          messages.GkerecommenderModelsFetchRequest()
      )
      if response.models:
        return response.models
      else:
        return []
    except apitools_exceptions.HttpError as error:
      raise api_lib_exceptions.HttpException(error, util.HTTP_ERROR_FORMAT)

  def Display(self, _, resources):
    if resources:
      log.out.Print("Supported models:")
      for model_name in resources:
        log.out.Print("- ", model_name)
    else:
      log.out.Print("No supported models found.")


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ListAlpha(commands.List):
  """List supported models."""

  def Run(self, _):
    client = util.GetClientInstance(base.ReleaseTrack.ALPHA)
    messages = util.GetMessagesModule(base.ReleaseTrack.ALPHA)

    try:
      response = client.models.List(messages.GkerecommenderModelsListRequest())
      if response.modelNames:
        return response.modelNames
      else:
        return []
    except exceptions.Error as e:
      log.error(f"An error has occurred: {e}")
      log.status.Print(f"An error has occured: {e}")
      return []

  def Display(self, _, resources):
    if resources:
      log.out.Print("Supported models:")
      for model_name in resources:
        log.out.Print("- ", model_name)
    else:
      log.out.Print("No supported models found.")
