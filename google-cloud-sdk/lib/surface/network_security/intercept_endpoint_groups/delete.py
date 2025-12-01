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
"""Delete endpoint group command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import datetime

from googlecloudsdk.api_lib.network_security.intercept_endpoint_groups import api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security.intercept import endpoint_group_flags

DETAILED_HELP = {
    'DESCRIPTION': """
          Delete a intercept endpoint group. Check the progress of endpoint group deletion
          by using `gcloud network-security intercept-endpoint-groups list`.

          For more examples, refer to the EXAMPLES section below.

        """,
    'EXAMPLES': """
            To delete a intercept endpoint group called `my-endpoint-group`, in project ID `my-project`, run:
            $ {command} my-endpoint-group --project=my-project --location=global

            OR

            $ {command} projects/my-project/locations/global/interceptEndpointGroups/my-endpoint-group

        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Delete(base.DeleteCommand):
  """Delete a Intercept Endpoint Group."""

  @classmethod
  def Args(cls, parser):
    endpoint_group_flags.AddEndpointGroupResource(cls.ReleaseTrack(), parser)
    endpoint_group_flags.AddMaxWait(
        parser, '20m'
    )  # default to 20 minutes wait.
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, True)

  def Run(self, args):
    client = api.Client(self.ReleaseTrack())

    endpoint_group = args.CONCEPTS.intercept_endpoint_group.Parse()

    is_async = args.async_
    max_wait = datetime.timedelta(seconds=args.max_wait)

    operation = client.DeleteEndpointGroup(
        name=endpoint_group.RelativeName(),
    )
    # Return the in-progress operation if async is requested.
    if is_async:
      # Delete operations have their returned resource in YAML format by
      # default, but here we want the operation metadata to be printed.
      if not args.IsSpecified('format'):
        args.format = 'default'
      return operation
    return client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message=(
            'waiting for intercept endpoint group [{}] to be deleted'.format(
                endpoint_group.RelativeName()
            )
        ),
        has_result=False,
        max_wait=max_wait,
    )


Delete.detailed_help = DETAILED_HELP
