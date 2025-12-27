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
"""Command for updating wire groups."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects.wire_groups import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.interconnects.cross_site_networks import flags as cross_site_network_flags
from googlecloudsdk.command_lib.compute.interconnects.wire_groups import flags
from googlecloudsdk.core import properties


_DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to update wire groups.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To disable a wire group, run:

        $ {command} example-wg --cross-site-network=example-csn --no-admin-enabled

        To change a wire group's unmetered bandwidth, run:

        $ {command} example-wg --cross-site-network=example-csn --bandwidth-unmetered=5

        To enable automatic failure detection for a wire group, run:

        $ {command} example-wg --cross-site-network=example-csn --fault-response=DISABLE_PORT

        To enable bandwidth sharing for a wire group, run:

        $ {command} example-wg --cross-site-network=example-csn --bandwidth-allocation=SHARED_WITH_WIRE_GROUP

        To update a wire group's description, run:

        $ {command} example-wg --cross-site-network=example-csn --description="new description"
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  """Update a Compute Engine wire group.

  *{command}* is used to update wire groups. A wire group represents a group of
  redundant wires.
  """

  # Framework override.
  detailed_help = _DETAILED_HELP

  WIRE_GROUP_ARG = None
  CROSS_SITE_NETWORK_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.WIRE_GROUP_ARG = flags.WireGroupArgument(plural=False)
    cls.WIRE_GROUP_ARG.AddArgument(parser, operation_type='update')
    cls.CROSS_SITE_NETWORK_ARG = (
        cross_site_network_flags.CrossSiteNetworkArgumentForOtherResource()
    )
    cls.CROSS_SITE_NETWORK_ARG.AddArgument(parser)
    flags.AddDescription(parser)
    flags.AddBandwidthUnmetered(parser, required=False)
    flags.AddBandwidthAllocation(parser, required=False)
    flags.AddFaultResponse(parser)
    flags.AddAdminEnabled(parser, update=True)
    flags.AddValidateOnly(parser)

  def Collection(self):
    return 'compute.wireGroups'

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.WIRE_GROUP_ARG.ResolveAsResource(
        args,
        holder.resources,
        default_scope=compute_scope.ScopeEnum.GLOBAL,
        additional_params={'crossSiteNetwork': args.cross_site_network},
    )

    project = properties.VALUES.core.project.GetOrFail()
    wire_group = client.WireGroup(
        ref,
        project,
        args.cross_site_network,
        compute_client=holder.client
    )

    return wire_group.Patch(
        description=args.description,
        wire_group_type=getattr(args, 'type', None),
        bandwidth_unmetered=args.bandwidth_unmetered,
        bandwidth_metered=getattr(args, 'bandwidth_metered', None),
        fault_response=args.fault_response,
        admin_enabled=args.admin_enabled,
        network_service_class=getattr(args, 'network_service_class', None),
        bandwidth_allocation=getattr(args, 'bandwidth_allocation', None),
        validate_only=args.validate_only,
    )


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(Update):
  """Update a Compute Engine wire group.

  *{command}* is used to update wire groups. A wire group represents a group of
  redundant wires.
  """

  @classmethod
  def Args(cls, parser):
    super(UpdateBeta, cls).Args(parser)
    flags.AddType(parser)


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(UpdateBeta):
  """Update a Compute Engine wire group.

  *{command}* is used to update wire groups. A wire group represents a group of
  redundant wires.
  """

  @classmethod
  def Args(cls, parser):
    super(UpdateAlpha, cls).Args(parser)
    flags.AddBandwidthMetered(parser)
    flags.AddNetworkServiceClass(parser)
