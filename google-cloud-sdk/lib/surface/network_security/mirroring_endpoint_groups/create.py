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
"""Create endpoint group command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import datetime

from googlecloudsdk.api_lib.network_security.mirroring_endpoint_groups import api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security import endpoint_group_flags
from googlecloudsdk.command_lib.util.args import labels_util

DETAILED_HELP = {
    'DESCRIPTION': """
          Create a mirroring endpoint group. Successful creation of an endpoint group results
          in an endpoint group in ACTIVE state. Check the progress of endpoint group creation
          by using `gcloud network-security mirroring-endpoint-groups list`.

          For more examples, refer to the EXAMPLES section below.

        """,
    'EXAMPLES': """
            To create a mirroring endpoint group called `my-endpoint-group`, in project ID `my-project`, run:
            $ {command} my-endpoint-group --project=my-project --location=global --mirroring-deployment-group=my-deployment-group

            OR

            $ {command} my-endpoint-group --project=my-project --location=global
            --mirroring-deployment-group=projects/my-project/locations/global/mirroringDeploymentGroups/my-deployment-group

            OR

            $ {command} projects/my-project/locations/global/mirroringEndpointGroups/my-endpoint-group
            --mirroring-deployment-group=projects/my-project/locations/global/mirroringDeploymentGroups/my-deployment-group

            OR

            $ {command} my-endpoint-group --project=my-project --location=global
            --mirroring-deployment-group=projects/my-project/locations/global/mirroringDeploymentGroups/my-deployment-group
            --description='new description'
        """,
}

_PACKET_BROKER_SUPPORTED = (base.ReleaseTrack.ALPHA,)


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Create(base.CreateCommand):
  """Create a Mirroring Endpoint Group."""

  @classmethod
  def Args(cls, parser):
    endpoint_group_flags.AddEndpointGroupResource(cls.ReleaseTrack(), parser)

    # Create the mutually exclusive group
    endpoint_group_flags.AddDeploymentGroupMutexGroup(
        cls.ReleaseTrack(), parser
    )

    endpoint_group_flags.AddMaxWait(
        parser,
        '20m',  # default to 20 minutes wait.
    )
    endpoint_group_flags.AddDescriptionArg(parser)
    if cls.ReleaseTrack() in _PACKET_BROKER_SUPPORTED:
      endpoint_group_flags.AddType(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, True)
    labels_util.AddCreateLabelsFlags(parser)

  def Run(self, args):
    client = api.Client(self.ReleaseTrack())
    endpoint_group = args.CONCEPTS.mirroring_endpoint_group.Parse()

    deployment_groups = None
    if args.IsSpecified('mirroring_deployment_group'):
      deployment_groups = (
          args.CONCEPTS.mirroring_deployment_group.Parse().RelativeName()
      )
    # Use getattr for safe access, as the flag only exists in ALPHA.
    elif getattr(args, 'mirroring_deployment_groups', None):
      deployment_groups = args.mirroring_deployment_groups

    labels = labels_util.ParseCreateArgs(
        args, client.messages.MirroringEndpointGroup.LabelsValue
    )

    is_async = args.async_
    max_wait = datetime.timedelta(seconds=args.max_wait)

    # endpoint_group.RelativeName() is the name
    # endpoint_group.Name() is the id
    operation = client.CreateEndpointGroup(
        endpoint_group_id=endpoint_group.Name(),
        parent=endpoint_group.Parent().RelativeName(),
        deployment_groups=deployment_groups,
        description=getattr(args, 'description', None),
        endpoint_group_type=getattr(args, 'type', None),
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
            'waiting for mirroring endpoint group [{}] to be created'.format(
                endpoint_group.RelativeName()
            )
        ),
        has_result=True,
        max_wait=max_wait,
    )


Create.detailed_help = DETAILED_HELP
