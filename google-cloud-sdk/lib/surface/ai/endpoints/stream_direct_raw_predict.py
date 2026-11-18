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
"""Vertex AI endpoints stream direct raw predict command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import base64

from googlecloudsdk.api_lib.ai.endpoints import prediction_streamer
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import constants
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.ai import endpoints_util
from googlecloudsdk.command_lib.ai import flags
from googlecloudsdk.command_lib.ai import region_util


def _AddArgs(parser):
  flags.AddEndpointResourceArg(
      parser,
      'to do online stream direct raw prediction',
      prompt_func=region_util.PromptForOpRegion,
  )
  flags.AddDirectRawPredictInputArg(parser)


def _Run(args, version):
  """Run Vertex AI online stream direct raw prediction."""
  endpoint_ref = args.CONCEPTS.endpoint.Parse()
  args.region = endpoint_ref.AsDict()['locationsId']
  with endpoint_util.AiplatformEndpointOverrides(
      version, region=args.region, is_prediction=True
  ):
    input_json = endpoints_util.ReadInputFromArgs(args.json_request)
    if version == constants.GA_VERSION:
      streamer = prediction_streamer.PredictionStreamer('v1')
    else:
      streamer = prediction_streamer.PredictionStreamer('v1beta1')

    if not args.IsSpecified('format'):
      args.format = 'json'

    for resp in streamer.StreamDirectRawPredict(
        endpoint=endpoint_ref.RelativeName(),
        method_name=input_json['method_name'],
        input=input_json['input'],
    ):
      resp.output = base64.b64decode(resp.output)
      yield resp


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class StreamDirectRawPredictGa(base.Command):
  """Run Vertex AI online stream direct raw prediction.

     `{command}` sends a stream direct raw prediction request to Vertex AI
     endpoint for the given input. The request limit is 10MB.

  ## EXAMPLES

  To stream direct predict against an endpoint ``123'' under project ``example''
  in region ``us-central1'', run:

    $ {command} 123 --project=example --region=us-central1
    --json-request=input.json
  """

  @staticmethod
  def Args(parser):
    _AddArgs(parser)

  def Run(self, args):
    return _Run(args, constants.GA_VERSION)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA)
class StreamDirectRawPredictBeta(StreamDirectRawPredictGa):
  """Run Vertex AI online stream direct raw prediction.

     `{command}` sends a stream direct raw prediction request to Vertex AI
     endpoint for the given input. The request limit is 10MB.

  ## EXAMPLES

  To stream direct raw predict against an endpoint ``123'' under project
  ``example'' in region ``us-central1'', run:

    $ {command} 123 --project=example --region=us-central1
    --json-request=input.json
  """

  def Run(self, args):
    return _Run(args, constants.BETA_VERSION)
