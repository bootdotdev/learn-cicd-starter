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
"""Update endpoint group association command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import datetime

from googlecloudsdk.api_lib.network_security.mirroring_endpoint_group_associations import api
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.network_security import endpoint_group_association_flags
from googlecloudsdk.command_lib.util.args import labels_util


DETAILED_HELP = {
    'DESCRIPTION': """
          Update a mirroring endpoint group association. Check the progress of association update
          by using `gcloud network-security mirroring-endpoint-group-associations list`.

          For examples refer to the EXAMPLES section below.
        """,
    'EXAMPLES': """
            To update labels k1 and k2, run:

            $ {command} my-association --project=my-project --location=global --update-labels=k1=v1,k2=v2

            To remove labels k3 and k4, run:

            $ {command} my-association --project=my-project --location=global --remove-labels=k3,k4

            To clear all labels from the mirroring endpoint group association, run:

            $ {command} my-association --project=my-project --location=global --clear-labels
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  """Update a Mirroring Endpoint Group Association."""

  _valid_arguments = [
      '--clear-labels',
      '--remove-labels',
      '--update-labels',
  ]

  @classmethod
  def Args(cls, parser):
    endpoint_group_association_flags.AddEndpointGroupAssociationResource(
        cls.ReleaseTrack(), parser
    )
    endpoint_group_association_flags.AddMaxWait(
        parser,
        '20m',  # default to 20 minutes wait.
    )
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, True)
    labels_util.AddUpdateLabelsFlags(parser)

  def Run(self, args):
    client = api.Client(self.ReleaseTrack())

    association = args.CONCEPTS.mirroring_endpoint_group_association.Parse()
    original = client.DescribeEndpointGroupAssociation(
        association.RelativeName()
    )
    self._validate_original_association(original)

    update_fields = {}
    labels = self._process_label_updates(client, args, original)
    if labels:
      update_fields['labels'] = labels

    if not update_fields:
      raise exceptions.MinimumArgumentException(self._valid_arguments)

    operation = client.UpdateEndpointGroupAssociation(
        name=association.RelativeName(),
        update_fields=update_fields,
    )

    # Returns the in-progress operation if async is requested.
    if args.async_:
      # Update operations have their returned resource in YAML format by
      # default, but here we want the operation metadata to be printed.
      if not args.IsSpecified('format'):
        args.format = 'default'
      return operation

    return self._wait_for_operation(
        client,
        operation,
        association,
        datetime.timedelta(seconds=args.max_wait),
    )

  def _validate_original_association(self, original):
    if original is None:
      raise exceptions.InvalidArgumentException(
          'mirroring-endpoint-group-association',
          'Mirroring endpoint group association does not exist.',
      )

  def _process_label_updates(self, client, args, original_association):
    """Processes the label update request.

    Args:
      client: the client to use to make the API call.
      args: the args from the command line.
      original_association: the original mirroring endpoint group association.

    Returns:
      the labels we would like to update if there is any update. Otherwise,
      it returns None.
    """
    labels_diff = labels_util.Diff.FromUpdateArgs(args)
    if not labels_diff.MayHaveUpdates():
      return None

    labels = original_association.labels
    labels_update = labels_diff.Apply(
        client.messages.MirroringEndpointGroupAssociation.LabelsValue,
        labels,
    )
    if labels_update.needs_update:
      return labels_update.labels

    return labels

  def _wait_for_operation(self, client, operation, association, max_wait):
    return client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message=(
            'waiting for mirroring endpoint group association [{}] to be'
            ' updated'.format(association.RelativeName())
        ),
        has_result=False,
        max_wait=max_wait,
    )


Update.detailed_help = DETAILED_HELP
