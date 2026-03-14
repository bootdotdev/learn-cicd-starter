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
"""Delete endpoint group association command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import datetime

from googlecloudsdk.api_lib.network_security.mirroring_endpoint_group_associations import api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security import endpoint_group_association_flags

DETAILED_HELP = {
    'DESCRIPTION': """
          Delete a mirroring endpoint group association. Check the progress of deletion
          by using `gcloud network-security mirroring-endpoint-group-associations list`.

          For more examples, refer to the EXAMPLES section below.

        """,
    'EXAMPLES': """
            To delete a mirroring endpoint group association called `my-association`, in project ID `my-project`, run:

            $ {command} my-association --project=my-project --location=global

            OR

            $ {command} projects/my-project/locations/global/mirroringEndpointGroupAssociations/my-association

        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
class Delete(base.DeleteCommand):
  """Delete a Mirroring Endpoint Group Association."""

  @classmethod
  def Args(cls, parser):
    endpoint_group_association_flags.AddEndpointGroupAssociationResource(
        cls.ReleaseTrack(), parser
    )
    endpoint_group_association_flags.AddMaxWait(
        parser, '20m'  # default to 20 minutes wait.
    )
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, True)

  def Run(self, args):
    client = api.Client(self.ReleaseTrack())

    association = args.CONCEPTS.mirroring_endpoint_group_association.Parse()

    is_async = args.async_
    max_wait = datetime.timedelta(seconds=args.max_wait)

    operation = client.DeleteEndpointGroupAssociation(
        name=association.RelativeName(),
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
            'waiting for mirroring endpoint group association [{}] to be'
            ' deleted'.format(association.RelativeName())
        ),
        has_result=False,
        max_wait=max_wait,
    )


Delete.detailed_help = DETAILED_HELP
