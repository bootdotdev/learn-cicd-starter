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
"""Command to update the specified message bus."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.eventarc import message_buses
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.eventarc import flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To update the message bus `my-message-bus` in location `us-central1`, run:

          $ {command} my-message-bus --location=us-central1

        To configure the message bus `my-message-bus` in location `us-central1` with a Cloud KMS CryptoKey, run:

          $ {command} my-message-bus --location=us-central1 --crypto-key=projects/PROJECT_ID/locations/KMS_LOCATION/keyRings/KEYRING/cryptoKeys/KEY

        """,
}


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Update(base.UpdateCommand):
  """Update an Eventarc message bus."""

  detailed_help = _DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    flags.AddMessageBusResourceArg(
        parser, 'Message bus to update.', required=True
    )
    flags.AddLoggingConfigArg(parser, 'The logging config of the message bus.')
    flags.AddCryptoKeyArg(parser, with_clear=True)
    labels_util.AddUpdateLabelsFlags(parser)
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run the update command."""
    client = message_buses.MessageBusClientV1()
    message_bus_ref = args.CONCEPTS.message_bus.Parse()

    log.debug(
        'Updating message bus {} for project {} in location {}'.format(
            message_bus_ref.messageBusesId,
            message_bus_ref.projectsId,
            message_bus_ref.locationsId,
        )
    )

    original_message_bus = client.Get(message_bus_ref)
    labels_update_result = labels_util.Diff.FromUpdateArgs(args).Apply(
        client.LabelsValueClass(), original_message_bus.labels
    )

    update_mask = client.BuildUpdateMask(
        logging_config=args.IsSpecified('logging_config'),
        crypto_key=args.IsSpecified('crypto_key'),
        clear_crypto_key=args.clear_crypto_key,
        labels=labels_update_result.needs_update,
    )

    operation = client.Patch(
        message_bus_ref,
        client.BuildMessageBus(
            message_bus_ref=message_bus_ref,
            logging_config=args.logging_config,
            crypto_key_name=args.crypto_key,
            labels=labels_update_result.GetOrNone(),
        ),
        update_mask,
    )

    if args.async_:
      return operation
    return client.WaitFor(operation, 'Updating', message_bus_ref)
