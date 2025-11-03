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
"""Command for spanner databases list user splits."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.spanner import database_splits
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.spanner import resource_args


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class List(base.ListCommand):
  """List split points that are added by a user to a Spanner database."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent(text="""\
        To list the user added split points of the given Spanner database,
        run:

          $ {command} my-database-id --instance=my-instance-id
        """),
  }

  @staticmethod
  def Args(parser):
    """See base class."""
    base.URI_FLAG.RemoveFromParser(parser)
    parser.display_info.AddFormat(DEFAULT_SPLIT_POINTS_FORMAT)
    resource_args.AddDatabaseResourceArg(
        parser, 'on which to list split points')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    return database_splits.ListSplitPoints(args.CONCEPTS.database.Parse())


DEFAULT_SPLIT_POINTS_FORMAT = """\
    table(
      TABLE_NAME,
      INDEX_NAME,
     INITIATOR,
     SPLIT_KEY,
     EXPIRE_TIME
    )"""
