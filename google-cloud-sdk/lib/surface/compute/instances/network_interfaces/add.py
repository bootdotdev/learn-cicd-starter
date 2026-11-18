# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
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
"""Command to add a dynamic network interface to a Compute Engine instance."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.instances import utils as instances_utils
from googlecloudsdk.api_lib.compute.operations import poller
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute import scope as compute_scopes
from googlecloudsdk.command_lib.compute.instances import flags as instances_flags
from googlecloudsdk.command_lib.compute.instances.network_interfaces import flags as network_interfaces_flags


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class Add(base.UpdateCommand):
  r"""Add a Dynamic Network Interface to a Compute Engine instance.

  *{command}* adds a Dynamic Network Interface to a Compute Engine instance.
  For example:

    $ {command} instance-name --parent-nic-name=nic1 --vlan=2
    --network=network-1 --subnetwork=subnetwork-1
  """

  enable_ipv6_assignment = False
  support_igmp_query = False

  @classmethod
  def Args(cls, parser):
    instances_flags.INSTANCE_ARG.AddArgument(parser)

    network_interfaces_flags.AddParentNicNameArg(parser)
    network_interfaces_flags.AddVlanArg(parser)
    network_interfaces_flags.AddNetworkArg(parser)
    network_interfaces_flags.AddSubnetworkArg(parser)
    network_interfaces_flags.AddPrivateNetworkIpArg(
        parser, add_network_interface=True
    )
    network_interfaces_flags.AddNetworkAttachmentArg(parser)
    network_interfaces_flags.AddAliasesArg(parser, add_network_interface=True)
    network_interfaces_flags.AddStackTypeArg(parser)
    network_interfaces_flags.AddNetworkTierArg(parser)
    network_interfaces_flags.AddIpv6NetworkTierArg(parser)
    network_interfaces_flags.AddAddressArgs(parser)
    network_interfaces_flags.AddExternalIpv6AddressArg(parser)
    network_interfaces_flags.AddExternalIpv6PrefixLengthArg(parser)
    network_interfaces_flags.AddInternalIpv6AddressArg(parser)
    network_interfaces_flags.AddInternalIpv6PrefixLengthArg(parser)
    if cls.enable_ipv6_assignment:
      network_interfaces_flags.AddIpv6AddressArg(parser)
      network_interfaces_flags.AddIpv6PrefixLengthArg(parser)

    if cls.support_igmp_query:
      network_interfaces_flags.AddIgmpQueryArg(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    compute_client = holder.client
    api_client = compute_client.apitools_client
    messages = compute_client.messages
    resources = holder.resources

    instance_ref = instances_flags.INSTANCE_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=flags.GetDefaultScopeLister(holder.client),
    )

    network_interface = instances_utils.CreateNetworkInterfaceMessage(
        resources,
        compute_client,
        network=getattr(args, 'network', None),
        subnet=getattr(args, 'subnetwork', None),
        project=instance_ref.project,
        location=instance_ref.zone,
        scope=compute_scopes.ScopeEnum.ZONE,
        network_attachment=getattr(args, 'network_attachment', None),
        parent_nic_name=getattr(args, 'parent_nic_name', None),
        vlan=getattr(args, 'vlan', None),
        private_network_ip=getattr(args, 'private_network_ip', None),
        alias_ip_ranges_string=getattr(args, 'aliases', None),
        stack_type=getattr(args, 'stack_type', None),
        network_tier=getattr(args, 'network_tier', None),
        ipv6_network_tier=getattr(args, 'ipv6_network_tier', None),
        address=getattr(args, 'address', None),
        no_address=getattr(args, 'no_address', None),
        external_ipv6_address=getattr(args, 'external_ipv6_address', None),
        external_ipv6_prefix_length=getattr(
            args, 'external_ipv6_prefix_length', None
        ),
        internal_ipv6_address=getattr(args, 'internal_ipv6_address', None),
        internal_ipv6_prefix_length=getattr(
            args, 'internal_ipv6_prefix_length', None
        ),
        ipv6_address=getattr(args, 'ipv6_address', None),
        ipv6_prefix_length=getattr(args, 'ipv6_prefix_length', None),
        igmp_query=getattr(args, 'igmp_query', None),
    )

    request = messages.ComputeInstancesAddNetworkInterfaceRequest(
        project=instance_ref.project,
        instance=instance_ref.instance,
        zone=instance_ref.zone,
        networkInterface=network_interface,
    )

    operation = api_client.instances.AddNetworkInterface(request)
    operation_ref = holder.resources.Parse(
        operation.selfLink, collection='compute.zoneOperations'
    )

    operation_poller = poller.Poller(api_client.instances)
    return waiter.WaitFor(
        operation_poller,
        operation_ref,
        f'Adding network interface for instance [{instance_ref.Name()}]',
    )


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class AddBeta(Add):
  r"""Add a Dynamic Network Interface to a Compute Engine instance.

  *{command}* adds a Dynamic Network Interface to a Compute Engine instance.
  For example:

    $ {command} instance-name --parent-nic-name=nic1 --vlan=2
    --network=network-1 --subnetwork=subnetwork-1
  """

  enable_ipv6_assignment = False
  support_igmp_query = False


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AddAlpha(AddBeta):
  r"""Add a Dynamic Network Interface to a Compute Engine instance.

  *{command}* adds a Dynamic Network Interface to a Compute Engine instance.
  For example:

    $ {command} instance-name --parent-nic-name=nic1 --vlan=2
    --network=network-1 --subnetwork=subnetwork-1
  """

  enable_ipv6_assignment = True
  support_igmp_query = True


Add.detailed_help = {
    'brief': 'Add a Dynamic Network Interface to a Compute Engine instance.',
    'DESCRIPTION': (
        '*{command}* adds a Dynamic Network Interface to a Compute Engine'
        ' instance.'
    ),
    'EXAMPLES': """\
      To add a Dynamic Network Interface to a Compute Engine instance, run:
        $ {command} instance-name --parent-nic-name=nic1 --vlan=2
        --network=network-1 --subnetwork=subnetwork-1
    """,
}
