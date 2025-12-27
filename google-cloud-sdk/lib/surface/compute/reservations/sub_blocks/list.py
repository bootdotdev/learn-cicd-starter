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

"""Command for listing reservation sub-blocks."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import request_helper
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.reservations import resource_args
from googlecloudsdk.command_lib.compute.reservations.sub_blocks import flags

DETAILED_HELP = {
    'DESCRIPTION':
        """\
        {command} displays all Compute Engine reservation sub-blocks in an extended reservation's block.
      """,
    'EXAMPLES':
        """\
        To list all reservation sub-blocks in an extended reservation's block my-block in table form,
        run:

        $ {command} extended-reservation --block-name=my-block --zone=us-central1-a --project=my-project

        To list the URIs of all reservation blocks in an extended reservation, run:

        $ {command} extended-reservation --block-name=my-block --zone=us-central1-a --project=my-project --uri
    """
}


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
class List(base.ListCommand):
  """List Compute Engine reservation sub-blocks."""

  detailed_help = DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    List.ReservationArg = resource_args.GetReservationResourceArg()
    List.ReservationArg.AddArgument(parser, operation_type='list')
    flags.AddListFlags(parser)

  def _Run(self, args, holder):
    client = holder.client

    reservation_ref = (
        List.ReservationArg.ResolveAsResource(
            args,
            holder.resources,
            default_scope=compute_scope.ScopeEnum.ZONE,
            scope_lister=compute_flags.GetDefaultScopeLister(client)))

    parent_name = f'reservations/{reservation_ref.reservation}/reservationBlocks/{args.block_name}'

    service = client.apitools_client.reservationSubBlocks
    request = (client.messages.
               ComputeReservationSubBlocksListRequest(
                   parentName=parent_name,
                   zone=reservation_ref.zone,
                   project=reservation_ref.project))

    errors = []
    results = list(request_helper.MakeRequests(
        requests=[(service, 'List', request)],
        http=client.apitools_client.http,
        batch_url=client.batch_url,
        errors=errors))

    if errors:
      utils.RaiseToolException(errors)
    return results

  def Run(self, args):
    """Creates and issues a reservationSubBlocks.list request.

    Args:
      args: the argparse arguments that this command was invoked with.

    Returns:
      List of reservation sub-blocks.
    """
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    return self._Run(args, holder)
