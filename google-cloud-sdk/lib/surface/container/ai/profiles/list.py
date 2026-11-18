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

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.ai.recommender import util
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import commands
from googlecloudsdk.command_lib.run.printers import profiles_csv_printer
from googlecloudsdk.command_lib.run.printers import profiles_printer_ga as profiles_printer
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


def amount_to_decimal(cost):
  """Converts cost to a decimal representation."""
  units = cost.units
  if not units:
    units = 0
  decimal_value = +(units + cost.nanos / 1e9)
  return f"{decimal_value:.3f}"


def get_decimal_cost(costs):
  """Returns the cost per million normalized output tokens as a decimal.

  Args:
    costs: The costs to convert.
  """
  output_token_cost = "N/A"
  if costs and costs[0].costPerMillionOutputTokens:
    output_token_cost = amount_to_decimal(
        costs[0].costPerMillionOutputTokens
    )
  input_token_cost = "N/A"
  if costs and costs[0].costPerMillionInputTokens:
    input_token_cost = amount_to_decimal(costs[0].costPerMillionInputTokens)
  return (input_token_cost, output_token_cost)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class List(commands.List):
  """List compatible accelerator profiles.

  This command lists all supported accelerators with their performance details.
  By default, the supported accelerators are displayed in a table format with
  select information for each accelerator. To see all details, use
  --format=yaml or --format=csvprofile.

  To get supported model, model servers, and model server versions, run `gcloud
  container ai profiles models list`, `gcloud container ai
  profiles model-servers list`, and `gcloud container ai profiles
  model-server-versions list`.
  """

  @staticmethod
  def Args(parser):
    parser.add_argument(
        "--model",
        help="The model.",
    )
    parser.add_argument(
        "--model-server",
        help=(
            "The model server version. Default is latest. Other options include"
            " the model server version of a profile, all which returns all"
            " versions."
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
        "--target-ntpot-milliseconds",
        type=int,
        help=(
            "The target normalized time per output token (NTPOT) in"
            " milliseconds. NTPOT is measured as the request_latency /"
            " output_tokens. If this field is set, the command will only return"
            " accelerators that can meet the target ntpot milliseconds and"
            " display their throughput performance at the target latency."
            " Otherwise, the command will return all accelerators and display"
            " their highest throughput performance."
        ),
    )
    parser.add_argument(
        "--target-ttft-milliseconds",
        type=int,
        help=(
            "The target time to first token (TTFT) in"
            " milliseconds. TTFT is measured as the request_latency /"
            " output_tokens. If this field is set, the command will only return"
            " profiles that can meet the target ttft milliseconds and"
            " display their throughput performance at the target latency."
            " Otherwise, the command will return all profiles and display"
            " their highest throughput performance."
        ),
    )
    parser.add_argument(
        "--target-cost-per-million-output-tokens",
        type=float,
        required=False,
        help=(
            "The target cost per million output tokens to filter profiles by,"
            " unit is 1 USD up to 5 decimal places."
        ),
    )
    parser.add_argument(
        "--target-cost-per-million-input-tokens",
        type=float,
        required=False,
        help=(
            "The target cost per million input tokens to filter profiles by,"
            " unit is 1 USD up to 5 decimal places."
        ),
    )
    parser.add_argument(
        "--pricing-model",
        required=False,
        type=str,
        help=(
            "The pricing model to use to calculate token cost. Currently, this"
            " supports on-demand, spot, 3-years-cud, 1-year-cud"
        ),
    )
    parser.add_argument(
        "--format",
        help=(
            "The output format. Default is profile, which displays the profile"
            " information in a table format, including cost conversions."
            " csvprofile displays the profile information in a CSV"
            " format.Options include csvprofile, profile, and yaml. "
        ),
    )

    resource_printer.RegisterFormatter(
        profiles_printer.PROFILES_PRINTER_FORMAT,
        profiles_printer.ProfilePrinter,
        hidden=True,
    )
    resource_printer.RegisterFormatter(
        profiles_csv_printer.PROFILES_PRINTER_FORMAT,
        profiles_csv_printer.ProfileCSVPrinter,
        hidden=True,
    )
    parser.display_info.AddFormat(profiles_printer.PROFILES_PRINTER_FORMAT)

  def Run(self, args):
    client = util.GetClientInstance(base.ReleaseTrack.GA)
    messages = util.GetMessagesModule(base.ReleaseTrack.GA)

    performance_requirements = messages.PerformanceRequirements()
    if args.target_ntpot_milliseconds:
      performance_requirements.targetNtpotMilliseconds = (
          args.target_ntpot_milliseconds
      )
    if args.target_ttft_milliseconds:
      performance_requirements.targetTtftMilliseconds = (
          args.target_ttft_milliseconds
      )

    if (
        args.target_cost_per_million_output_tokens
        or args.target_cost_per_million_input_tokens
        or args.pricing_model
    ):
      cost = messages.Cost()
      if args.target_cost_per_million_output_tokens:
        units, nanos = decimal_to_amount(
            args.target_cost_per_million_output_tokens
        )
        cost.costPerMillionOutputTokens = messages.Amount(
            units=units, nanos=nanos
        )
      if args.target_cost_per_million_input_tokens:
        units, nanos = decimal_to_amount(
            args.target_cost_per_million_input_tokens
        )
        cost.costPerMillionInputTokens = messages.Amount(
            units=units, nanos=nanos
        )
      if args.pricing_model:
        cost.pricingModel = args.pricing_model
      performance_requirements.targetCost = cost
    try:
      request = messages.FetchProfilesRequest(
          model=args.model,
          modelServer=args.model_server,
          modelServerVersion=args.model_server_version,
      )
      if (
          performance_requirements.targetNtpotMilliseconds is not None
          or performance_requirements.targetTtftMilliseconds is not None
          or performance_requirements.targetCost is not None
      ):
        request.performanceRequirements = performance_requirements

      response = client.profiles.Fetch(request)
      if response.profile:
        return response.profile
      else:
        return []
    except apitools_exceptions.HttpError as error:
      raise exceptions.HttpException(error, util.HTTP_ERROR_FORMAT)
