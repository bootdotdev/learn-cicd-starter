# -*- coding: utf-8 -*- #
# Copyright 2022 Google LLC. All Rights Reserved.
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

"""Command for creating spokes."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_connectivity import networkconnectivity_api
from googlecloudsdk.api_lib.network_connectivity import networkconnectivity_util
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_connectivity import flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log
from googlecloudsdk.core import resources


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
class Create(base.Command):
  """Create a new VPC spoke.

  Create a new VPC spoke.
  """

  @staticmethod
  def Args(parser):
    flags.AddSpokeResourceArg(
        parser, 'to create', flags.ResourceLocationType.GLOBAL_ONLY
    )
    flags.AddRegionGroup(parser, hide_global_arg=False, hide_region_arg=True)
    flags.AddHubFlag(parser)
    flags.AddGroupFlag(parser)
    flags.AddVPCNetworkFlag(parser)
    flags.AddDescriptionFlag(parser, 'Description of the spoke to create.')
    flags.AddAsyncFlag(parser)
    flags.AddExcludeExportRangesFlag(
        parser, hide_exclude_export_ranges_flag=False
    )
    flags.AddIncludeExportRangesFlag(
        parser, hide_include_export_ranges_flag=False
    )
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

      spoke = client.messages.GoogleCloudNetworkconnectivityV1betaSpoke(
          hub=args.hub,
          group=args.group,
          linkedVpcNetwork=client.messages.GoogleCloudNetworkconnectivityV1betaLinkedVpcNetwork(
              uri=args.vpc_network,
              excludeExportRanges=args.exclude_export_ranges,
              includeExportRanges=args.include_export_ranges,
          ),
          description=args.description,
          labels=labels,
      )
      op_ref = client.CreateSpokeBeta(spoke_ref, spoke)
    else:
      labels = labels_util.ParseCreateArgs(
          args, client.messages.Spoke.LabelsValue
      )

      spoke = client.messages.Spoke(
          hub=args.hub,
          group=args.group,
          linkedVpcNetwork=client.messages.LinkedVpcNetwork(
              uri=args.vpc_network,
              excludeExportRanges=args.exclude_export_ranges,
              includeExportRanges=args.include_export_ranges,
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
  To create a VPC spoke named ``myspoke'', run:

    $ {command} myspoke --hub="https://www.googleapis.com/networkconnectivity/v1/projects/my-project/locations/global/hubs/my-hub" --global --vpc-network="https://www.googleapis.com/compute/v1/projects/my-project/global/networks/my-vpc"
  """,
    'API REFERENCE': """ \
  This command uses the networkconnectivity/v1 API. The full documentation
  for this API can be found at:
  https://cloud.google.com/network-connectivity/docs/reference/networkconnectivity/rest
  """,
}
