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
"""Create endpoint group association command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import datetime

from googlecloudsdk.api_lib.network_security.mirroring_endpoint_group_associations import api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security import endpoint_group_association_flags
from googlecloudsdk.command_lib.util.args import labels_util

DETAILED_HELP = {
    'DESCRIPTION': """
          Create a mirroring endpoint group association. Successful creation of an association results
          in an association in ACTIVE state. Check the progress of association creation
          by using `gcloud network-security mirroring-endpoint-group-associations list`.

          For more examples, refer to the EXAMPLES section below.

        """,
    'EXAMPLES': """
            To create a mirroring endpoint group association called `my-association`, in project ID `my-project`, run:

            $ {command} my-association --project=my-project --location=global --mirroring-endpoint-group=my-endpoint-group --network=my-network

            OR

            $ {command} my-association --project=my-project --location=global --mirroring-endpoint-group=my-endpoint-group --network=projects/my-project/global/networks/my-network

            OR

            $ {command} projects/my-project/locations/global/mirroringEndpointGroupAssociations/my-association --mirroring-endpoint-group=projects/my-project/locations/global/mirroringEndpointGroups/my-endpoint-group --network=projects/my-project/global/networks/my-network

        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
class Create(base.CreateCommand):
  """Create a Mirroring Endpoint Group Association."""

  @classmethod
  def Args(cls, parser):
    endpoint_group_association_flags.AddEndpointGroupAssociationResource(
        cls.ReleaseTrack(), parser
    )
    endpoint_group_association_flags.AddMirroringEndpointGroupResource(
        cls.ReleaseTrack(), parser
    )
    endpoint_group_association_flags.AddNetworkResource(parser)
    endpoint_group_association_flags.AddMaxWait(
        parser,
        '20m',  # default to 20 minutes wait.
    )
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, True)
    labels_util.AddCreateLabelsFlags(parser)

  def Run(self, args):
    client = api.Client(self.ReleaseTrack())

    association = args.CONCEPTS.mirroring_endpoint_group_association.Parse()
    mirroring_endpoint_group = args.CONCEPTS.mirroring_endpoint_group.Parse()
    network = args.CONCEPTS.network.Parse()
    labels = labels_util.ParseCreateArgs(
        args, client.messages.MirroringEndpointGroupAssociation.LabelsValue
    )

    is_async = args.async_
    max_wait = datetime.timedelta(seconds=args.max_wait)

    operation = client.CreateEndpointGroupAssociation(
        association_id=association.Name(),
        parent=association.Parent().RelativeName(),
        mirroring_endpoint_group=mirroring_endpoint_group.RelativeName(),
        network=network.RelativeName(),
        labels=labels,
    )
    # Return the in-progress operation if async is requested.
    if is_async:
      # Create operations have their returned resource in YAML format by
      # default, but here we want the operation metadata to be printed.
      if not args.IsSpecified('format'):
        args.format = 'default'
      return operation
    return client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message=(
            'waiting for mirroring endpoint group association [{}] to be'
            ' created'.format(association.RelativeName())
        ),
        has_result=True,
        max_wait=max_wait,
    )


Create.detailed_help = DETAILED_HELP
