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
"""Command for describing reservation sub-blocks."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.reservations import resource_args
from googlecloudsdk.command_lib.compute.reservations.sub_blocks import flags


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
class Describe(base.DescribeCommand):
  """Describe a Compute Engine reservation sub-block."""

  @staticmethod
  def Args(parser):
    Describe.ReservationArg = (
        resource_args.GetReservationResourceArg()
    )
    Describe.ReservationArg.AddArgument(parser, operation_type='describe')
    flags.AddDescribeFlags(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    reservation_ref = Describe.ReservationArg.ResolveAsResource(
        args,
        holder.resources,
        default_scope=compute_scope.ScopeEnum.ZONE,
        scope_lister=compute_flags.GetDefaultScopeLister(client))

    parent_name = f'reservations/{reservation_ref.reservation}/reservationBlocks/{args.block_name}'

    request = (
        client.messages.ComputeReservationSubBlocksGetRequest(
            parentName=parent_name,
            zone=reservation_ref.zone,
            project=reservation_ref.project,
            reservationSubBlock=args.sub_block_name,)
    )

    return client.MakeRequests([(client.apitools_client.reservationSubBlocks,
                                 'Get', request)])[0]


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class DescribeAlpha(Describe):
  """Describe a Compute Engine reservation sub-block."""

  @staticmethod
  def Args(parser):
    Describe.Args(parser)
    flags.AddFullViewFlag(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    reservation_ref = Describe.ReservationArg.ResolveAsResource(
        args,
        holder.resources,
        default_scope=compute_scope.ScopeEnum.ZONE,
        scope_lister=compute_flags.GetDefaultScopeLister(client))

    parent_name = f'reservations/{reservation_ref.reservation}/reservationBlocks/{args.block_name}'

    view_enum = None
    if args.IsSpecified('full_view'):
      view_enum_type = (
          client.messages.ComputeReservationSubBlocksGetRequest.ViewValueValuesEnum
      )
      view_enum = view_enum_type(args.full_view)
    request = (
        client.messages.ComputeReservationSubBlocksGetRequest(
            parentName=parent_name,
            zone=reservation_ref.zone,
            project=reservation_ref.project,
            reservationSubBlock=args.sub_block_name,
            view=view_enum,)
    )

    return client.MakeRequests([(client.apitools_client.reservationSubBlocks,
                                 'Get', request)])[0]


Describe.detailed_help = {
    'EXAMPLES':
        """\
    To describe a reservation sub-block in reservation exr1 in my-zone
    with block name my-block and sub-block name my-sub-block, run:

      $ {command} exr1 --zone=my-zone --block-name=my-block --sub-block-name=my-sub-block
    """,
}
