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

"""Command for creating Gateway spokes."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_connectivity import networkconnectivity_api
from googlecloudsdk.api_lib.network_connectivity import networkconnectivity_util
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_connectivity import flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log
from googlecloudsdk.core import resources


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class Create(base.Command):
  """Create a new Gateway spoke.

  Create a new Gateway spoke.
  """

  @staticmethod
  def Args(parser):
    messages = apis.GetMessagesModule('networkconnectivity', 'v1beta')

    flags.AddSpokeResourceArg(
        parser, 'to create', flags.ResourceLocationType.REGION_ONLY
    )
    flags.AddRegionFlag(
        parser, supports_region_wildcard=False, hidden=False, required=True
    )
    flags.AddHubFlag(parser)
    flags.AddGroupFlag(parser, required=True)
    flags.AddDescriptionFlag(parser, 'Description of the spoke to create.')
    flags.AddAsyncFlag(parser)
    flags.AddLandingNetworkFlag(parser)
    flags.AddCapacityFlag(
        messages.GoogleCloudNetworkconnectivityV1betaGateway, parser
    )
    flags.AddIpRangeReservationsFlag(parser)
    labels_util.AddCreateLabelsFlags(parser)

  def Run(self, args):
    client = networkconnectivity_api.SpokesClient(
        release_track=self.ReleaseTrack()
    )

    spoke_ref = args.CONCEPTS.spoke.Parse()

    if self.ReleaseTrack() == base.ReleaseTrack.BETA:
      labels = labels_util.ParseCreateArgs(
          args,
          client.messages.GoogleCloudNetworkconnectivityV1betaSpoke.LabelsValue,
      )

      range_reservations = [
          client.messages.GoogleCloudNetworkconnectivityV1betaIpRangeReservation(
              ipRange=ip_range
          )
          for ip_range in args.ip_range_reservations
      ]

      if args.landing_network:
        landing_network = (
            client.messages.GoogleCloudNetworkconnectivityV1betaLandingNetwork(
                network=args.landing_network
            )
        )
      else:
        landing_network = None

      spoke = client.messages.GoogleCloudNetworkconnectivityV1betaSpoke(
          hub=args.hub,
          group=args.group,
          gateway=client.messages.GoogleCloudNetworkconnectivityV1betaGateway(
              capacity=flags.GetCapacityArg(
                  client.messages.GoogleCloudNetworkconnectivityV1betaGateway
              ).GetEnumForChoice(args.capacity),
              landingNetwork=landing_network,
              ipRangeReservations=range_reservations,
          ),
          description=args.description,
          labels=labels,
      )
      op_ref = client.CreateSpokeBeta(spoke_ref, spoke)
    else:
      labels = labels_util.ParseCreateArgs(
          args, client.messages.Spoke.LabelsValue
      )

      range_reservations = [
          client.messages.IpRangeReservation(ipRange=ip_range)
          for ip_range in args.ip_range_reservations
      ]

      if args.landing_network:
        landing_network = client.messages.LandingNetwork(
            network=args.landing_network
        )
      else:
        landing_network = None

      spoke = client.messages.Spoke(
          hub=args.hub,
          group=args.group,
          gateway=client.messages.Gateway(
              capacity=flags.GetCapacityArg(
                  client.messages.Gateway
              ).GetEnumForChoice(args.capacity),
              landingNetwork=landing_network,
              ipRangeReservations=range_reservations,
          ),
          description=args.description,
          labels=labels,
      )
      op_ref = client.CreateSpoke(spoke_ref, spoke)

    log.status.Print('Create request issued for: [{}]'.format(spoke_ref.Name()))

    if op_ref.done:
      log.CreatedResource(spoke_ref.Name(), kind='spoke')
      return op_ref

    if args.async_:
      log.status.Print('Check operation [{}] for status.'.format(op_ref.name))
      return op_ref

    op_resource = resources.REGISTRY.ParseRelativeName(
        op_ref.name,
        collection='networkconnectivity.projects.locations.operations',
        api_version=networkconnectivity_util.VERSION_MAP[self.ReleaseTrack()],
    )
    poller = waiter.CloudOperationPoller(
        client.spoke_service, client.operation_service
    )
    res = waiter.WaitFor(
        poller,
        op_resource,
        'Waiting for operation [{}] to complete'.format(op_ref.name),
    )
    log.CreatedResource(spoke_ref.Name(), kind='spoke')
    return res


Create.detailed_help = {
    'EXAMPLES': """ \
  To create a Gateway spoke named ``myspoke'' in us-central1, with a capacity of 10 Gbps and IP range reservations of 10.1.1.0/24

    $ {command} myspoke --hub=my-hub --region us-central1 --group gateways --capacity 10g --ip-range-reservations 10.1.1.0/24

  To create a Gateway spoke named ``myspoke'' in us-central1, with a capacity of 10 Gbps, IP range reservations of 10.1.1.0/24 and 10.1.2.0/24, and a landing network of my-vpc, run:

    $ {command} myspoke --hub=my-hub --region us-central1 --group gateways --capacity 10g --ip-range-reservations 10.1.1.0/24,10.1.2.0/24  --landing-network my-vpc
  """,
    'API REFERENCE': """ \
  This command uses the networkconnectivity/v1 API. The full documentation
  for this API can be found at:
  https://cloud.google.com/network-connectivity/docs/reference/networkconnectivity/rest
  """,
}
