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
"""Outputs benchmarking data for GKE Inference Quickstart."""

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.ai.recommender import util
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import commands
from googlecloudsdk.command_lib.run.printers import profiles_csv_printer
from googlecloudsdk.core.resource import resource_printer


_EXAMPLE = """
To get benchmarking data for a given model and model server, run:

$ {command} --model=google/gemma-2-27b-it --model-server=vllm --pricing-model=spot
"""


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
    output_token_cost = amount_to_decimal(costs[0].costPerMillionOutputTokens)
  input_token_cost = "N/A"
  if costs and costs[0].costPerMillionInputTokens:
    input_token_cost = amount_to_decimal(costs[0].costPerMillionInputTokens)
  return (input_token_cost, output_token_cost)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class List(commands.List):
  """List benchmarks for a given model and model server.

  This command lists all benchmarking data for a given model and model server.
  By default, the benchmarks are displayed in a CSV format.

  For examples of visualizing the benchmarking data, see the accompanying Colab
  notebook:
  https://colab.research.google.com/github/GoogleCloudPlatform/kubernetes-engine-samples/blob/main/ai-ml/notebooks/giq_visualizations.ipynb
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
        help="The model server.",
    )
    parser.add_argument(
        "--model-server-version",
        help=(
            "The model server version. Default is latest. Other options include"
            " the model server version of a profile, all which returns all"
            " versions."
        ),
    )
    parser.add_argument(
        "--instance-type",
        help=(
            "The instance type. If not specified, this defaults to any"
            "instance type."
        ),
    )
    parser.add_argument(
        "--format",
        help=(
            "The format to print the output in. Default is csvprofile, which"
            " displays the profile information in a CSV format, including"
            "cost conversions."
        ),
    )

    parser.add_argument(
        "--pricing-model",
        required=False,
        help=(
            "The pricing model to use to calculate token cost. Currently, this"
            " supports on-demand, spot, 3-years-cud, 1-year-cud"
        ),
    )

    resource_printer.RegisterFormatter(
        profiles_csv_printer.PROFILES_PRINTER_FORMAT,
        profiles_csv_printer.ProfileCSVPrinter,
    )
    parser.display_info.AddFormat(profiles_csv_printer.PROFILES_PRINTER_FORMAT)

  def Run(self, args):
    client = util.GetClientInstance(base.ReleaseTrack.GA)
    messages = util.GetMessagesModule(base.ReleaseTrack.GA)

    try:
      model_server_info = messages.ModelServerInfo(
          model=args.model,
          modelServer=args.model_server,
          modelServerVersion=args.model_server_version,
      )
      request = messages.FetchBenchmarkingDataRequest(
          modelServerInfo=model_server_info,
          instanceType=args.instance_type,
          pricingModel=args.pricing_model,
      )
      response = client.benchmarkingData.Fetch(request)
      if not response.profile:
        return []
      else:
        return response.profile
    except apitools_exceptions.HttpError as error:
      raise exceptions.HttpException(error, util.HTTP_ERROR_FORMAT)
