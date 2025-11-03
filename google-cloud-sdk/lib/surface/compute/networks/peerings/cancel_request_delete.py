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
"""Command for cancelling a network peering deletion request."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.core import properties


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CancelRequestDelete(base.Command):
  r"""Cancel deletion request of a Compute Engine network peering.

  *{command}* is used to cancel a request to delete a consensus network peering
  connection between two networks.

  ## EXAMPLES
    To cancel a deletion request of a consensus peering with the name
    'peering-name' between the network 'local-network' and the network
    'peer-network', run:

        $ {command} peering-name --network=local-network

        $ {command} peering-name --network=peer-network
  """

  @classmethod
  def ArgsCommon(cls, parser):
    parser.add_argument('name', help='The name of the peering.')
    parser.add_argument(
        '--network',
        required=True,
        help=(
            'The name of the network in the current project containing the '
            'peering.'
        ),
    )
    base.ASYNC_FLAG.AddToParser(parser)

  @classmethod
  def Args(cls, parser):
    cls.ArgsCommon(parser)

  def Run(self, args):
    """Issues the request necessary for cancelling deletion request of the peering."""
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    request = client.messages.ComputeNetworksCancelRequestRemovePeeringRequest(
        network=args.network,
        networksCancelRequestRemovePeeringRequest=(
            client.messages.NetworksCancelRequestRemovePeeringRequest(
                name=args.name
            )
        ),
        project=properties.VALUES.core.project.GetOrFail(),
    )

    return client.MakeRequests([(
        client.apitools_client.networks,
        'CancelRequestRemovePeering',
        request,
    )])
