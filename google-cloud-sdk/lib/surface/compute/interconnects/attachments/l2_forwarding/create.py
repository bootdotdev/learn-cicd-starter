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
"""Command for creating L2 forwarding interconnect attachments."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects.attachments import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.interconnects import flags as interconnect_flags
from googlecloudsdk.command_lib.compute.interconnects.attachments import flags as attachment_flags
from googlecloudsdk.command_lib.compute.networks import flags as network_flags
from googlecloudsdk.core import log

_DOCUMENTATION_LINK = 'https://cloud.google.com/interconnect/docs/how-to/l2-forwarding/creating-l2-attachments'


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Create(base.CreateCommand):
  """Create a Compute Engine L2 forwarding interconnect attachment.

  *{command}* is used to create a L2 forwarding interconnect attachments. An
  interconnect attachment is what binds the underlying connectivity of an
  interconnect to a path into and out of the customer's cloud network.
  """
  INTERCONNECT_ATTACHMENT_ARG = None
  INTERCONNECT_ARG = None
  NETWORK_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.INTERCONNECT_ARG = (
        interconnect_flags.InterconnectArgumentForOtherResource(
            'The interconnect for the interconnect attachment'))
    cls.INTERCONNECT_ARG.AddArgument(parser)

    cls.NETWORK_ARG = network_flags.NetworkArgumentForOtherResource(
        'The Google Network to use for L2 forwarding.'
    )
    cls.NETWORK_ARG.AddArgument(parser)

    cls.INTERCONNECT_ATTACHMENT_ARG = (
        attachment_flags.InterconnectAttachmentArgument())
    cls.INTERCONNECT_ATTACHMENT_ARG.AddArgument(parser, operation_type='create')
    attachment_flags.AddDescription(parser)
    attachment_flags.AddEnableAdmin(parser)
    attachment_flags.AddBandwidth(parser, required=False)
    attachment_flags.AddMtu(parser)
    attachment_flags.AddGeneveVni(parser)
    attachment_flags.AddDefaultApplianceIpAddress(parser)
    attachment_flags.AddTunnelEndpointIpAddress(parser)
    attachment_flags.AddZ2zVlan(parser)
    attachment_flags.AddDryRun(parser)

  def _Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    attachment_ref = self.INTERCONNECT_ATTACHMENT_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(holder.client))

    interconnect_attachment = client.InterconnectAttachment(
        attachment_ref, compute_client=holder.client)

    interconnect_ref = None
    if args.interconnect is not None:
      interconnect_ref = self.INTERCONNECT_ARG.ResolveAsResource(
          args, holder.resources)

    if args.network is not None:
      network_ref = self.NETWORK_ARG.ResolveAsResource(args, holder.resources)
    else:
      network_ref = None

    return interconnect_attachment.Create(
        description=args.description,
        interconnect=interconnect_ref,
        attachment_type='L2_DEDICATED',
        admin_enabled=args.enable_admin,
        bandwidth=getattr(args, 'bandwidth', None),
        validate_only=getattr(args, 'dry_run', None),
        mtu=getattr(args, 'mtu', None),
        network=network_ref,
        geneve_vni=getattr(args, 'geneve_vni', None),
        default_appliance_ip_address=getattr(
            args, 'default_appliance_ip_address', None
        ),
        tunnel_endpoint_ip_address=getattr(
            args, 'tunnel_endpoint_ip_address', None
        ),
        vlan_tag_802_1q=getattr(args, 'z2z_vlan', None),
    )

  def Epilog(self, resources_were_displayed):
    message = (
        'You must ensure that there is at least one valid Appliance IP '
        '(default or within the mapping) and that firewall rules allow '
        'traffic between the tunnel endpoint IP and your appliance(s). '
        'See also {} for more detailed help.'.format(_DOCUMENTATION_LINK)
    )
    log.status.Print(message)

  def Run(self, args):
    """See base.CreateCommand."""
    return self._Run(args)
