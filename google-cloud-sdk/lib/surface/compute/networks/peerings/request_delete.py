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
"""Command for creating network peerings."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.core import properties


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class RequestDelete(base.Command):
  r"""Request deletion of a Compute Engine network peering.

  *{command}* is used to request deletion of a consensus peering between virtual
    networks. The peering can be deleted if both sides request deletion.

  ## EXAMPLES
    To request deletion of a consensus peering with the name 'peering-name'
    between the network 'local-network' and the network 'peer-network', run:

        $ {command} peering-name --network=local-network

        $ {command} peering-name --network=peer-network

    To complete the deletion, run gcloud compute networks peerings delete
    for each side of the peering.
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
    """Issues the request necessary for requesting deletion of the peering."""
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    request = client.messages.ComputeNetworksRequestRemovePeeringRequest(
        network=args.network,
        networksRequestRemovePeeringRequest=(
            client.messages.NetworksRequestRemovePeeringRequest(name=args.name)
        ),
        project=properties.VALUES.core.project.GetOrFail(),
    )

    return client.MakeRequests(
        [(client.apitools_client.networks, 'RequestRemovePeering', request)]
    )
