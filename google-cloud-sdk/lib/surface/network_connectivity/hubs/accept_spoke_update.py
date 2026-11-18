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

"""Command for accepting spoke updates."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_connectivity import networkconnectivity_api
from googlecloudsdk.api_lib.network_connectivity import networkconnectivity_util
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_connectivity import flags
from googlecloudsdk.core import log
from googlecloudsdk.core import resources


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
class AcceptSpokeUpdate(base.Command):
  """Accept a proposal to update a spoke in a hub.

  Accept a proposed or previously rejected VPC spoke update. By accepting a
  spoke update, you permit updating connectivity between the associated VPC
  network and other VPC networks that are attached to the same hub.
  """

  @staticmethod
  def Args(parser):
    flags.AddHubResourceArg(parser, 'to accept the spoke update')
    flags.AddSpokeFlag(parser, 'URI of the spoke to accept update')
    flags.AddSpokeEtagFlag(parser, 'Etag of the spoke to accept update')
    flags.AddAsyncFlag(parser)

  def Run(self, args):
    client = networkconnectivity_api.HubsClient(
        release_track=self.ReleaseTrack()
    )
    hub_ref = args.CONCEPTS.hub.Parse()
    if self.ReleaseTrack() == base.ReleaseTrack.BETA:
      op_ref = client.AcceptSpokeUpdateBeta(
          hub_ref, args.spoke, args.spoke_etag
      )
    else:
      op_ref = client.AcceptSpokeUpdate(hub_ref, args.spoke, args.spoke_etag)

    log.status.Print(
        'Accept spoke update request issued for: [{}]'.format(hub_ref.Name())
    )

    op_resource = resources.REGISTRY.ParseRelativeName(
        op_ref.name,
        collection='networkconnectivity.projects.locations.operations',
        api_version=networkconnectivity_util.VERSION_MAP[self.ReleaseTrack()],
    )
    poller = waiter.CloudOperationPollerNoResources(client.operation_service)

    if op_ref.done:
      return poller.GetResult(op_resource)

    if args.async_:
      log.status.Print('Check operation [{}] for status.'.format(op_ref.name))
      return op_ref

    res = waiter.WaitFor(
        poller, op_resource,
        'Waiting for operation [{}] to complete'.format(op_ref.name))
    return res


AcceptSpokeUpdate.detailed_help = {
    'EXAMPLES':
        """ \
  To accept updating a spoke named ``my-spoke'' with ``etag'' in a hub named ``my-hub'', run:

    $ {command} my-hub --spoke="projects/spoke-project/locations/global/hubs/my-spoke" --spoke-etag=etag
  """,
    'API REFERENCE':
        """ \
  This command uses the networkconnectivity/v1 API. The full documentation
  for this API can be found at:
  https://cloud.google.com/network-connectivity/docs/reference/networkconnectivity/rest
  """,
}
