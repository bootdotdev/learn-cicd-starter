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
"""Command to list all pipelines in a project and location."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.eventarc import pipelines
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.eventarc import flags

_DETAILED_HELP = {
    "DESCRIPTION": "{description}",
    "EXAMPLES": """\
        To list all pipelines in location ``us-central1'', run:

          $ {command} --location=us-central1

        To list all pipelines in all locations, run:

          $ {command} --location=-

        or

          $ {command}
        """,
}

_FORMAT = """\
table(
    name.scope("pipelines"):label=NAME,
    name.scope("locations").segment(0):label=LOCATION,
    loggingConfig.logSeverity:label=LOGGING_CONFIG,
    inputPayloadFormat():label=INPUT_PAYLOAD_FORMAT,
    retryPolicy.maxAttempts:label=MAX_RETRY_ATTEMPTS,
    retryPolicy.minRetryDelay:label=MIN_RETRY_DELAY,
    retryPolicy.maxRetryDelay:label=MAX_RETRY_DELAY
)
"""


def _InputPayloadFormat(pipeline):
  """Generate an input payload format string for the pipeline."""
  input_payload_format = pipeline.get("inputPayloadFormat")
  if input_payload_format is None:
    return "None"
  if input_payload_format.get("json") is not None:
    return "Json"
  if input_payload_format.get("avro") is not None:
    return "Avro"
  if input_payload_format.get("protobuf") is not None:
    return "Protobuf"
  return "Unknown Format"


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class List(base.ListCommand):
  """List Eventarc pipelines."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    flags.AddLocationResourceArg(
        parser,
        "Location for which to list pipelines. This should be one of the"
        " supported regions.",
        required=False,
        allow_aggregation=True,
    )
    flags.AddProjectResourceArg(parser)
    parser.display_info.AddFormat(_FORMAT)
    parser.display_info.AddUriFunc(pipelines.GetPipelineURI)
    parser.display_info.AddTransforms({
        "inputPayloadFormat": _InputPayloadFormat,
    })

  def Run(self, args):
    client = pipelines.PipelineClientV1()
    location_ref = args.CONCEPTS.location.Parse()
    return client.List(location_ref, args.limit, args.page_size)
