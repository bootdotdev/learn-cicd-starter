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

"""Command for adding endpoints to a wire group."""

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
        *{command}* is used to add endpoints to a wire group.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To add an endpoint to a wire group, run:

          $ {command} example-wg \
              --cross-site-network=example-csn \
              --endpoint-label=endpoint-1
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class AddEndpoint(base.UpdateCommand):
  """Add endpoint to a Compute Engine wire group.

  *{command}* adds endpoint to a Compute Engine wire group.
  """

  # Framework override.
  detailed_help = _DETAILED_HELP

  WIRE_GROUP_ARG = None
  CROSS_SITE_NETWORK_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.CROSS_SITE_NETWORK_ARG = (
        cross_site_network_flags.CrossSiteNetworkArgumentForOtherResource()
    )
    cls.CROSS_SITE_NETWORK_ARG.AddArgument(parser)
    cls.WIRE_GROUP_ARG = flags.WireGroupArgument(plural=False)
    cls.WIRE_GROUP_ARG.AddArgument(parser, operation_type='update')
    flags.AddEndpointLabel(parser)

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

    self._messages = holder.client.messages

    wire_group = client.WireGroup(
        ref=ref,
        project=project,
        cross_site_network=args.cross_site_network,
        compute_client=holder.client,
        resources=holder.resources,
    )
    endpoint_label = args.endpoint_label
    endpoints = wire_group.Describe().endpoints

    endpoints_map = convert_endpoints_to_dict(endpoints)

    endpoints_map[endpoint_label] = holder.client.messages.WireGroupEndpoint()

    endpoints = _build_endpoint_messages(self._messages, endpoints_map)

    return wire_group.Patch(
        endpoints=endpoints,
    )


def convert_endpoints_to_dict(endpoints):
  """Extracts the key,value pairs from the additionalProperties attribute.

  Creates a python dict to be able to pass them into the client.

  Args:
    endpoints: the list of additionalProperties messages

  Returns:
    Python dictionary containing the key value pairs.
  """
  endpoints_map = {}

  if not endpoints or not endpoints.additionalProperties:
    return endpoints_map

  for endpoint_property in endpoints.additionalProperties:
    key, value = endpoint_property.key, endpoint_property.value
    endpoints_map[key] = value

  return endpoints_map


def _build_endpoint_messages(messages, endpoints_map):
  """Builds a WireGroup.EndpointValue message.

  This is so we can re-assign them to the additionalProperties attribute on
  the WireGroup.EndpointsValue message.

  Args:
    messages: the messages module
    endpoints_map: map of endpoints with label as the key and the
      endpoint message as the value

  Returns:
    WireGroup.EndpointsValue message
  """
  endpoint_properties_list = []

  for endpoint_label, endpoints_message in endpoints_map.items():
    endpoint_properties_list.append(
        messages.WireGroup.EndpointsValue.AdditionalProperty(
            key=endpoint_label,
            value=endpoints_message,
        )
    )

  return messages.WireGroup.EndpointsValue(
      additionalProperties=endpoint_properties_list
  )
