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
"""Vertex AI endpoints direct raw predict command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import base64

from googlecloudsdk.api_lib.ai.endpoints import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import constants
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.ai import endpoints_util
from googlecloudsdk.command_lib.ai import flags
from googlecloudsdk.command_lib.ai import region_util


def _AddArgs(parser):
  flags.AddEndpointResourceArg(
      parser,
      'to do online direct raw prediction',
      prompt_func=region_util.PromptForOpRegion,
  )
  flags.AddDirectRawPredictInputArg(parser)


def _Run(args, version):
  """Run Vertex AI online direct raw prediction."""
  endpoint_ref = args.CONCEPTS.endpoint.Parse()
  args.region = endpoint_ref.AsDict()['locationsId']
  with endpoint_util.AiplatformEndpointOverrides(
      version, region=args.region, is_prediction=True
  ):
    endpoints_client = client.EndpointsClient(version=version)

    # Decode the base64 encoded input, because it will be encoded by the
    # apitools client.
    input_json = endpoints_util.ReadInputFromArgs(args.json_request)
    input_json['input'] = base64.b64decode(input_json['input']).decode('utf-8')
    if version == constants.GA_VERSION:
      results = endpoints_client.DirectRawPredict(endpoint_ref, input_json)
    else:
      results = endpoints_client.DirectRawPredictBeta(endpoint_ref, input_json)

    # Decode the base64 encoded output.
    results.output = base64.b64decode(results.output)

    if not args.IsSpecified('format'):
      # default format is based on the response.
      args.format = endpoints_util.GetDefaultFormat(
          results.output, key_name='output'
      )
    return results


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class DirectRawPredictGa(base.Command):
  """Run Vertex AI online direct raw prediction.

     `{command}` sends a direct raw prediction request to Vertex AI endpoint for
     the given input. The request limit is 10MB.

  ## EXAMPLES

  To direct predict against an endpoint ``123'' under project ``example'' in
  region ``us-central1'', run:

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
class DirectRawPredictBeta(DirectRawPredictGa):
  """Run Vertex AI online direct raw prediction.

     `{command}` sends a direct raw prediction request to Vertex AI endpoint for
     the given input. The request limit is 10MB.

  ## EXAMPLES

  To direct raw predict against an endpoint ``123'' under project ``example'' in
  region ``us-central1'', run:

    $ {command} 123 --project=example --region=us-central1
    --json-request=input.json
  """

  def Run(self, args):
    return _Run(args, constants.BETA_VERSION)
