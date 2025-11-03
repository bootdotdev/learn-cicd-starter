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
"""Create deployment group command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import datetime

from googlecloudsdk.api_lib.network_security.intercept_deployment_groups import api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security.intercept import deployment_group_flags
from googlecloudsdk.command_lib.util.args import labels_util

DETAILED_HELP = {
    'DESCRIPTION': """
          Create an intercept deployment group. Successful creation of a deployment group results
          in a deployment group in ACTIVE state. Check the progress of deployment group creation
          by using `gcloud network-security intercept-deployment-groups list`.

          For more examples, refer to the EXAMPLES section below.

        """,
    'EXAMPLES': """
            To create a intercept deployment group called `my-deployment-group`, in project ID `my-project`, run:
            $ {command} my-deployment-group --project=my-project --location=global --network=my-network

            OR

            $ {command} my-deployment-group --project=my-project --location=global
            --network=projects/my-project/global/networks/my-network

            OR

            $ {command} projects/my-project/locations/global/interceptDeploymentGroups/my-deployment-group
            --network=projects/my-project/global/networks/my-network

            OR

            $ {command} projects/my-project/locations/global/interceptDeploymentGroups/my-deployment-group
            --network=projects/my-project/global/networks/my-network --description='new description'

        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Create(base.CreateCommand):
  """Create an Intercept Deployment Group."""

  @classmethod
  def Args(cls, parser):
    deployment_group_flags.AddDeploymentGroupResource(
        cls.ReleaseTrack(), parser
    )
    deployment_group_flags.AddNetworkResource(parser)
    deployment_group_flags.AddMaxWait(
        parser,
        '20m',  # default to 20 minutes wait.
    )
    deployment_group_flags.AddDescriptionArg(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, True)
    labels_util.AddCreateLabelsFlags(parser)

  def Run(self, args):
    client = api.Client(self.ReleaseTrack())

    deployment_group = args.CONCEPTS.intercept_deployment_group.Parse()
    network = args.CONCEPTS.network.Parse()
    labels = labels_util.ParseCreateArgs(
        args, client.messages.InterceptDeploymentGroup.LabelsValue
    )

    is_async = args.async_
    max_wait = datetime.timedelta(seconds=args.max_wait)

    # deployment_group.RelativeName() is the name
    # deployment_group.Name() is the id
    operation = client.CreateDeploymentGroup(
        deployment_group_id=deployment_group.Name(),
        parent=deployment_group.Parent().RelativeName(),
        network=network.RelativeName(),
        labels=labels,
        description=getattr(args, 'description', None),
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
            'waiting for intercept deployment group [{}] to be created'.format(
                deployment_group.RelativeName()
            )
        ),
        has_result=True,
        max_wait=max_wait,
    )


Create.detailed_help = DETAILED_HELP
