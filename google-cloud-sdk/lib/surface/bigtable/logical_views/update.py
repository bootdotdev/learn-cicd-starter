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
"""Bigtable logical views list command."""

import textwrap

from googlecloudsdk.api_lib.bigtable import logical_views
from googlecloudsdk.api_lib.bigtable import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.bigtable import arguments
from googlecloudsdk.core import log


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.GA, base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA
)
class UpdateLogicalView(base.UpdateCommand):
  """Update a Bigtable logical view."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          To update a logical view to a new query, run:

            $ {command} my-logical-view-id --instance=my-instance-id --query="SELECT my-column-family2 FROM my-table"

          To enable deletion protection on a logical view, run:

            $ {command} my-logical-view-id --instance=my-instance-id --deletion-protection

          """),
  }

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    arguments.AddLogicalViewResourceArg(parser, 'to update')
    # At least one of query or deletion_protection must be specified.
    update_group = parser.add_group(required=True)
    arg_adder = arguments.ArgAdder(update_group)
    arg_adder.AddDeletionProtection()
    arg_adder.AddViewQuery()
    arguments.ArgAdder(parser).AddAsync()

  def _UpdateLogicalView(self, logical_view_ref, args):
    """Updates a logical view with the given arguments.

    Args:
      logical_view_ref: A resource reference of the new logical view.
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Long running operation.
    """
    return logical_views.Update(
        logical_view_ref, args.query, args.deletion_protection
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Updated resource.
    """
    logical_view_ref = args.CONCEPTS.logical_view.Parse()
    operation = self._UpdateLogicalView(logical_view_ref, args)
    if not args.async_:
      operation_ref = util.GetOperationRef(operation)
      return util.AwaitLogicalView(
          operation_ref,
          'Updating logical view {0}'.format(logical_view_ref.Name()),
      )

    log.UpdatedResource(
        logical_view_ref.Name(), kind='logical view', is_async=args.async_
    )
    return None
