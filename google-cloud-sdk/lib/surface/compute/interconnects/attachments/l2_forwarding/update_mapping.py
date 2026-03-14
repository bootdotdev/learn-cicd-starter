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

"""Command for updating member interconnects to an interconnect L2-forwarding attachment innner vlan to appliance mappings."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects.attachments import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.interconnects.attachments import flags as attachment_flags
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateMapping(base.UpdateCommand):
  """Update vlan to ip mapping rule to an L2-forwarding attachment.

  *{command}* update vlan to ip mapping rule to an L2-forwarding attachment.
  """

  INTERCONNECT_ATTACHMENT_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.INTERCONNECT_ATTACHMENT_ARG = (
        attachment_flags.InterconnectAttachmentArgument())
    cls.INTERCONNECT_ATTACHMENT_ARG.AddArgument(parser, operation_type='create')
    attachment_flags.AddVlanKey(parser, required=True)
    attachment_flags.AddApplianceIpAddress(parser)
    attachment_flags.AddApplianceName(parser)
    attachment_flags.AddInnerVlanToApplianceMappings(parser)

  def _Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    attachment_ref = self.INTERCONNECT_ATTACHMENT_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(holder.client))

    interconnect_attachment = client.InterconnectAttachment(
        attachment_ref, compute_client=holder.client)

    old_mapping = interconnect_attachment.DescribeMapping(args.vlan_key)
    if not old_mapping:
      log.status.Print(
          'Mapping with vlan key {} does not exist'.format(args.vlan_key)
      )
      return None

    return interconnect_attachment.UpdateMapping(
        vlan_key=args.vlan_key,
        appliance_name=getattr(args, 'appliance_name', None),
        appliance_ip_address=getattr(args, 'appliance_ip_address', None),
        inner_vlan_to_appliance_mappings=getattr(
            args, 'inner_vlan_to_appliance_mappings', None
        ),
    )

  def Run(self, args):
    """See base.UpdateCommand."""
    return self._Run(args)
