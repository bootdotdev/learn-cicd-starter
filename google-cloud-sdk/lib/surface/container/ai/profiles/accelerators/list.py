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
"""Lists compatible accelerator profiles for GKE Inference Quickstart."""

from googlecloudsdk.api_lib.ai.recommender import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import commands
from googlecloudsdk.command_lib.run.printers import profiles_printer
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core.resource import resource_printer

_EXAMPLES = """
To list compatible accelerator profiles for a model, run:

$ {command} --model=deepseek-ai/DeepSeek-R1-Distill-Qwen-7B
"""


def decimal_to_amount(decimal_value):
  """Converts a decimal representation to an Amount proto."""

  units = int(decimal_value)
  nanos = int((decimal_value - units) * 1e9)

  return (units, nanos)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class List(commands.List):
  """List compatible accelerator profiles.

  This command lists all supported accelerators with their performance details.
  By default, the supported accelerators are displayed in a table format with
  select information for each accelerator. To see all details, use
  --format=yaml.

  To get supported model, model servers, and model server versions, run `gcloud
  alpha container ai profiles models list`, `gcloud alpha container ai
  profiles model-servers list`, and `gcloud alpha container ai profiles
  model-server-versions list`.
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
        help=(
            "The model server. If not specified, this defaults to any model"
            " server."
        ),
    )
    parser.add_argument(
        "--model-server-version",
        help=(
            "The model server version. If not specified, this defaults to the"
            " latest version."
        ),
    )
    parser.add_argument(
        "--max-ntpot-milliseconds",
        type=int,
        help=(
            "The maximum normalized time per output token (NTPOT) in"
            " milliseconds. NTPOT is measured as the request_latency /"
            " output_tokens. If this field is set, the command will only return"
            " accelerators that can meet the target ntpot milliseconds and"
            " display their throughput performance at the target latency."
            " Otherwise, the command will return all accelerators and display"
            " their highest throughput performance."
        ),
    )

    parser.add_argument(
        "--target-cost-per-million-output-tokens",
        hidden=True,
        type=float,
        required=False,
        help=(
            "The target cost per million output tokens to filter profiles by,"
            " unit is 1 USD up to 5 decimal places."
        ),
    )
    parser.add_argument(
        "--target-cost-per-million-input-tokens",
        hidden=True,
        type=float,
        required=False,
        help=(
            "The target cost per million input tokens to filter profiles by,"
            " unit is 1 USD up to 5 decimal places."
        ),
    )
    parser.add_argument(
        "--pricing-model",
        hidden=True,
        required=False,
        type=str,
        help=(
            "The pricing model to use to calculate token cost. Currently, this"
            " supports on-demand, spot, 3-years-cud, 1-year-cud"
        ),
    )

    parser.add_argument(
        "--format",
        type=str,
        help="The format to use for the output. Default is table. yaml|table",
    )

    resource_printer.RegisterFormatter(
        profiles_printer.PROFILES_PRINTER_FORMAT,
        profiles_printer.ProfilePrinter,
        hidden=True,
    )
    parser.display_info.AddFormat(profiles_printer.PROFILES_PRINTER_FORMAT)
    parser.display_info.AddFormat(
        "table("
        "acceleratorType,"
        "modelAndModelServerInfo.modelName,"
        "modelAndModelServerInfo.modelServerName,"
        "modelAndModelServerInfo.modelServerVersion,"
        "resourcesUsed.acceleratorCount,"
        "performanceStats.outputTokensPerSecond,"
        "performanceStats.ntpotMilliseconds"
        ")"
    )

  def Run(self, args):
    client = util.GetClientInstance(base.ReleaseTrack.ALPHA)
    messages = util.GetMessagesModule(base.ReleaseTrack.ALPHA)

    try:
      request = messages.GkerecommenderAcceleratorsListRequest(
          modelName=args.model,
          modelServerName=args.model_server,
          modelServerVersion=args.model_server_version,
          performanceRequirements_maxNtpotMilliseconds=args.max_ntpot_milliseconds,
          performanceRequirements_cost_pricingModel=args.pricing_model,
      )
      if args.target_cost_per_million_output_tokens:
        units, nanos = decimal_to_amount(
            args.target_cost_per_million_output_tokens
        )
        request.performanceRequirements_cost_costPerMillionNormalizedOutputTokens_units = (
            units
        )
        request.performanceRequirements_cost_costPerMillionNormalizedOutputTokens_nanos = (
            nanos
        )
      if args.target_cost_per_million_input_tokens:
        units, nanos = decimal_to_amount(
            args.target_cost_per_million_input_tokens
        )
        request.performanceRequirements_cost_costPerMillionInputTokens_units = (
            units
        )
        request.performanceRequirements_cost_costPerMillionInputTokens_nanos = (
            nanos
        )
      response = client.accelerators.List(request)
      self.comments = response.comments
      if response:
        return response
      else:
        return []
    except exceptions.Error as e:
      log.error(f"An error has occurred: {e}")
      log.status.Print(f"An error has occurred: {e}")
      return []
