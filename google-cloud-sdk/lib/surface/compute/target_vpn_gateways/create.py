# -*- coding: utf-8 -*- #
# Copyright 2014 Google LLC. All Rights Reserved.
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
"""Command for creating target VPN Gateways."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import resource_manager_tags_utils
from googlecloudsdk.command_lib.compute.networks import flags as network_flags
from googlecloudsdk.command_lib.compute.target_vpn_gateways import flags
import six


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class Create(base.CreateCommand):
  """Create a Cloud VPN Classic Target VPN Gateway.

    *{command}* is used to create a Cloud VPN Classic Target VPN Gateway. A
  Target VPN Gateway can reference one or more VPN tunnels that connect it to
  the remote tunnel endpoint. A Target VPN Gateway may also be referenced by
  one or more forwarding rules that define which packets the
  gateway is responsible for routing.
  """

  NETWORK_ARG = None
  TARGET_VPN_GATEWAY_ARG = None
  _support_tagging_at_creation = False

  @classmethod
  def Args(cls, parser):
    """Adds arguments to the supplied parser."""
    parser.display_info.AddFormat(flags.DEFAULT_LIST_FORMAT)
    cls.NETWORK_ARG = network_flags.NetworkArgumentForOtherResource(
        """\
        A reference to a network in this project to
        contain the VPN Gateway.
        """)
    cls.NETWORK_ARG.AddArgument(parser)
    cls.TARGET_VPN_GATEWAY_ARG = flags.TargetVpnGatewayArgument()
    cls.TARGET_VPN_GATEWAY_ARG.AddArgument(parser, operation_type='create')

    parser.add_argument(
        '--description',
        help='An optional, textual description for the target VPN Gateway.')
    if cls._support_tagging_at_creation:
      parser.add_argument(
          '--resource-manager-tags',
          type=arg_parsers.ArgDict(),
          metavar='KEY=VALUE',
          help="""\
            A comma-separated list of Resource Manager tags to apply to the target VPN gateway.
        """,
      )

    parser.display_info.AddCacheUpdater(flags.TargetVpnGatewaysCompleter)

  def _Run(self, args):
    """Issues API requests to construct Target VPN Gateways.

    Args:
      args: argparse.Namespace, The arguments received by this command.

    Returns:
      [protorpc.messages.Message], A list of responses returned
      by the compute API.
    """
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = client.messages
    # helper = target_vpn_gateways_utils.TargetVpnGatewayHelper(holder)

    target_vpn_gateway_ref = self.TARGET_VPN_GATEWAY_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client))
    network_ref = self.NETWORK_ARG.ResolveAsResource(args, holder.resources)

    params = None
    if self._support_tagging_at_creation:
      if args.resource_manager_tags is not None:
        params = self._CreateTargetVpnGatewayParams(
            messages, args.resource_manager_tags
        )

    if self._support_tagging_at_creation and params is not None:
      request = client.messages.ComputeTargetVpnGatewaysInsertRequest(
          project=target_vpn_gateway_ref.project,
          region=target_vpn_gateway_ref.region,
          targetVpnGateway=client.messages.TargetVpnGateway(
              description=args.description,
              name=target_vpn_gateway_ref.Name(),
              network=network_ref.SelfLink(),
              params=params,
          ),
      )
    else:
      request = client.messages.ComputeTargetVpnGatewaysInsertRequest(
          project=target_vpn_gateway_ref.project,
          region=target_vpn_gateway_ref.region,
          targetVpnGateway=client.messages.TargetVpnGateway(
              description=args.description,
              name=target_vpn_gateway_ref.Name(),
              network=network_ref.SelfLink(),
          ),
      )
    return client.MakeRequests(
        [(client.apitools_client.targetVpnGateways, 'Insert', request)]
    )

  def _CreateTargetVpnGatewayParams(self, messages, resource_manager_tags):
    resource_manager_tags_map = (
        resource_manager_tags_utils.GetResourceManagerTags(
            resource_manager_tags
        )
    )
    params = messages.TargetVpnGatewayParams
    additional_properties = [
        params.ResourceManagerTagsValue.AdditionalProperty(key=key, value=value)
        for key, value in sorted(six.iteritems(resource_manager_tags_map))
    ]
    return params(
        resourceManagerTags=params.ResourceManagerTagsValue(
            additionalProperties=additional_properties
        )
    )

  def Run(self, args):
    """Issues API requests to construct Target VPN gateways."""
    return self._Run(args)


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateBeta(Create):
  """Create a Cloud VPN Classic Target VPN Gateway.

    *{command}* is used to create a Cloud VPN Classic Target VPN Gateway. A
  Target VPN Gateway can reference one or more VPN tunnels that connect it to
  the remote tunnel endpoint. A Target VPN Gateway may also be referenced by
  one or more forwarding rules that define which packets the
  gateway is responsible for routing.
  """

  _support_tagging_at_creation = False

  @classmethod
  def Args(cls, parser):
    """Set up arguments for this command."""
    super(CreateBeta, cls).Args(parser)

  def Run(self, args):
    """See base.CreateCommand."""
    return self._Run(args)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateAlpha(Create):
  """Create a Cloud VPN Classic Target VPN Gateway.

    *{command}* is used to create a Cloud VPN Classic Target VPN Gateway. A
  Target VPN Gateway can reference one or more VPN tunnels that connect it to
  the remote tunnel endpoint. A Target VPN Gateway may also be referenced by
  one or more forwarding rules that define which packets the
  gateway is responsible for routing.
  """

  _support_tagging_at_creation = True

  @classmethod
  def Args(cls, parser):
    """Set up arguments for this command."""
    super(CreateAlpha, cls).Args(parser)

  def Run(self, args):
    """See base.CreateCommand."""
    return self._Run(args)
