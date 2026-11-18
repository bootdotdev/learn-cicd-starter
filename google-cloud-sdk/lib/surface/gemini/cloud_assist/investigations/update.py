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

"""Command to create a new investigation."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import datetime

from googlecloudsdk.api_lib.gemini_cloud_assist import args as gca_args
from googlecloudsdk.api_lib.gemini_cloud_assist import util as gca_util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.core.util import times


@base.DefaultUniverseOnly
class Create(base.Command):
  r"""Update an existing investigation.

  Shows metadata for the investigation after updating.

  This command can fail for the following reasons:
  * The investigation ID doesn't exist.
  * The active account does not have permission to update the investigation.
  * The investigation is currently running.

  ## EXAMPLES

  The following command updates title, text description, resources, and start
  time of the existing investigation with the name`example-foo-bar-1`:

    $ {command} example-foo-bar-1 --title="Example Investigation" \
        --issue="I have a problem" --start-time=2025-07-10
  """

  @staticmethod
  def Args(parser):
    gca_args.AddInvestigationResourceArg(
        parser, verb="to update", required=True, allow_no_id=False
    )
    parser.display_info.AddFormat("value(investigation_markdown_detailed())")
    parser.add_argument(
        "--issue",
        required=False,
        help=(
            "A description of the issue you are investigating, or an error log."
        ),
    )

    start_time_group = parser.add_mutually_exclusive_group(sort_args=False)
    start_time_group.add_argument(
        "--start-time",
        required=False,
        type=times.ParseDateTime,
        help="The estimated start time of the issue you are investigating.",
    )
    start_time_group.add_argument(
        "--clear-start-time",
        required=False,
        action="store_true",
        help="Clear the start time of the investigation.",
    )

    end_time_group = parser.add_mutually_exclusive_group(sort_args=False)
    end_time_group.add_argument(
        "--end-time",
        required=False,
        type=times.ParseDateTime,
        help="The estimated end time of the issue you are investigating.",
    )
    end_time_group.add_argument(
        "--clear-end-time",
        required=False,
        action="store_true",
        help="Clear the end time of the investigation.",
    )

    title_group = parser.add_mutually_exclusive_group(sort_args=False)
    title_group.add_argument(
        "--title",
        required=False,
        help="The desired title of the resulting investigation.",
    )
    title_group.add_argument(
        "--clear-title",
        required=False,
        action="store_true",
        help="Clear the title of the investigation.",
    )

    resources_group = parser.add_mutually_exclusive_group(sort_args=False)
    resources_group.add_argument(
        "--resources",
        required=False,
        metavar="RESOURCE",
        type=arg_parsers.ArgList(),
        help="A list of resources relevant to the investigation",
    )
    resources_group.add_argument(
        "--clear-resources",
        required=False,
        action="store_true",
        help="Clear the resources of the investigation.",
    )

  def Run(self, args):
    investigation_ref = args.CONCEPTS.investigation.Parse()
    updated_investigation = gca_util.UpdateInvestigation(
        investigation_ref,
        "" if args.clear_title else args.title,
        args.issue,
        datetime.datetime.min if args.clear_start_time else args.start_time,
        datetime.datetime.max if args.clear_end_time else args.end_time,
        [] if args.clear_resources else args.resources,
    )
    return gca_util.RunInvestigationRevisionBlocking(
        updated_investigation.revision
    )
