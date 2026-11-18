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
"""Command for performing maintenance on a reservation block."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.reservations import resource_args
from googlecloudsdk.command_lib.compute.reservations import util
from googlecloudsdk.command_lib.compute.reservations.blocks import flags


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
class PerformMaintenance(base.UpdateCommand):
  """Perform maintenance on a reservation block within a reservation."""

  @staticmethod
  def Args(parser):
    resource_args.GetReservationResourceArg().AddArgument(
        parser, operation_type='perform-maintenance')
    flags.AddDescribeFlags(parser)
    flags.AddScopeFlags(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    reservation_ref = resource_args.GetReservationResourceArg(
    ).ResolveAsResource(
        args,
        holder.resources,
        default_scope=compute_scope.ScopeEnum.ZONE,
        scope_lister=compute_flags.GetDefaultScopeLister(client))

    request = (
        client.messages.ComputeReservationBlocksPerformMaintenanceRequest(
            reservation=reservation_ref.reservation,
            zone=reservation_ref.zone,
            project=reservation_ref.project,
            reservationBlock=args.block_name,
            reservationsBlocksPerformMaintenanceRequest=
            client.messages.ReservationsBlocksPerformMaintenanceRequest(
                maintenanceScope=util.MakeReservationBlocksMaintenanceScope(
                    client.messages, args.scope))
        )
    )

    return client.MakeRequests([(client.apitools_client.reservationBlocks,
                                 'PerformMaintenance', request)])

PerformMaintenance.detailed_help = {
    'EXAMPLES':
        """\
    To perform maintenance on a reservation block in reservation my-reservation
    in my-zone with block name my-reservation-block-0001 with scope all, run:

      $ {command} my-reservation --zone=my-zone --block-name=my-reservation-block-0001 --scope=all
    """,
}
