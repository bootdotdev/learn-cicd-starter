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
"""Command to create a message bus."""

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
        To create a new message bus `my-message-bus` in location `us-central1`, run:

          $ {command} my-message-bus --location=us-central1
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Create(base.CreateCommand):
  """Create an Eventarc message bus."""

  detailed_help = _DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    flags.AddMessageBusResourceArg(
        parser, 'The message bus to create.', required=True
    )
    flags.AddLoggingConfigArg(parser, 'The logging config of the message bus.')
    flags.AddCryptoKeyArg(parser, with_clear=False, hidden=False)
    labels_util.AddCreateLabelsFlags(parser)
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run the create command."""
    client = message_buses.MessageBusClientV1()
    message_bus_ref = args.CONCEPTS.message_bus.Parse()

    log.debug(
        'Creating message bus {} for project {} in location {}'.format(
            message_bus_ref.messageBusesId,
            message_bus_ref.projectsId,
            message_bus_ref.locationsId,
        )
    )
    operation = client.Create(
        message_bus_ref,
        client.BuildMessageBus(
            message_bus_ref,
            args.logging_config,
            args.crypto_key,
            labels_util.ParseCreateArgs(args, client.LabelsValueClass()),
        ),
    )

    if args.async_:
      return operation
    return client.WaitFor(operation, 'Creating', message_bus_ref)
