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
"""Command for spanner databases add splits."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.spanner import database_splits
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.spanner import flags
from googlecloudsdk.command_lib.spanner import resource_args


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Add(base.UpdateCommand):
  """Add split points to a  Spanner database."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
        To add split points to the given Spanner database, run:

          $ {command} my-database-id --instance=my-instance-id
              --splits-file=path/to/splits.txt --initiator=my-initiator-string
              --split-expiration-date=2024-08-15T15:55:10Z
        """),
  }

  @staticmethod
  def Args(parser):
    """See base class."""
    resource_args.AddDatabaseResourceArg(parser, 'on which to add split points')
    flags.SplitsFile(
        help_text=(
            'The path of a file containing split points to add to the database.'
            ' Separate split points in the file with a new line. The file'
            ' format is <ObjectType>[space]<ObjectName>[space]<Split Value>,'
            ' where the ObjectType is one of TABLE or INDEX and the Split Value'
            ' is the split point key. For index, the split point key is the'
            ' index key with or without a full table key prefix.'
        )
    ).AddToParser(parser)
    flags.SplitExpirationDate(
        help_text=(
            'The date when the split points become system managed and'
            ' becomes eligible for merging. The default is 10 days from the'
            ' date of creation. The maximum is 30 days from the date of'
            ' creation.'
        )
    ).AddToParser(parser)
    flags.Initiator(
        help_text=(
            'The tag to identify the initiator of the split points.'
        )
    ).AddToParser(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    return database_splits.AddSplitPoints(
        args.CONCEPTS.database.Parse(),
        flags.GetSplitPoints(args),
        args.initiator,
    )
