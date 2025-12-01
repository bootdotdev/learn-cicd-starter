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

from googlecloudsdk.api_lib.gemini_cloud_assist import args as gca_args
from googlecloudsdk.api_lib.gemini_cloud_assist import util as gca_util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.core.util import times


@base.DefaultUniverseOnly
class Create(base.Command):
  """Create a new investigation.

  Shows metadata for the newly created investigation after creation.

  This command can fail for the following reasons:
  * The chosen investigation ID, if specified, already exists.
  * The active account does not have permission to create investigations in the
  project.

  ## EXAMPLES

  The following command creates a new investigation with the ID and some basic
  information
  `example-foo-bar-1`:

    $ {command} example-foo-bar-1 --title="Example Investigation" --issue="I
    have a problem" --start-time=2025-07-10
  """

  @staticmethod
  def Args(parser):
    gca_args.AddInvestigationResourceArg(
        parser, verb="to create", required=False, allow_no_id=True
    )
    parser.display_info.AddFormat("value(investigation_markdown_detailed())")
    parser.add_argument(
        "--issue",
        required=True,
        help=(
            "A description of the issue you are investigating, or an error log."
        ),
    )
    parser.add_argument(
        "--start-time",
        required=False,
        type=times.ParseDateTime,
        help="The estimated start time of the issue you are investigating.",
    )
    parser.add_argument(
        "--end-time",
        required=False,
        type=times.ParseDateTime,
        help="The estimated end time of the issue you are investigating.",
    )
    parser.add_argument(
        "--title",
        required=False,
        help="The desired title of the resulting investigation.",
    )
    parser.add_argument(
        "--resources",
        required=False,
        metavar="RESOURCE",
        type=arg_parsers.ArgList(),
        help="A list of resources relevant to the investigation",
    )

  def Run(self, args):
    investigation_ref = args.CONCEPTS.investigation.Parse()
    created_investigation = gca_util.CreateInvestigation(
        investigation_ref,
        args.title,
        args.issue,
        args.start_time,
        args.end_time,
        args.resources,
    )
    return gca_util.RunInvestigationRevisionBlocking(
        created_investigation.revision
    )
