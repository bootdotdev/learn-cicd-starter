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
"""Command to publish on message buses."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.eventarc import message_buses
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.eventarc import flags
from googlecloudsdk.core import log

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To publish an event to the message bus `my-message-bus` with event id `1234`, event type `event-provider.event.v1.eventType`, event source `//event-provider/event/source`, event data `{ "key": "value" }` and  event attributes of `attribute1=value`, run:

          $ {command} my-message-bus --location=us-central1 --event-id=1234 --event-type=event-provider.event.v1.eventType --event-source="//event-provider/event/source" --event-data='{"key": "value"}' --event-attributes=attribute1=value

        To publish an event to the message bus `my-message-bus` with a json message, run:

          $ {command} my-message-bus --location=us-central1 --json-message='{"id": 1234, "type": "event-provider.event.v1.eventType", "source": "//event-provider/event/source", "specversion": "1.0", "data": {"key": "value"}}'
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Publish(base.Command):
  """Publish to an Eventarc message bus."""

  detailed_help = _DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    flags.AddMessageBusResourceArg(
        parser, 'Message bus to publish to.', required=True
    )
    flags.AddMessageBusPublishingArgs(parser)

  def Run(self, args):
    """Run the Publish command."""

    client = message_buses.MessageBusClientV1()
    message_bus_ref = args.CONCEPTS.message_bus.Parse()

    log.debug(
        'Publishing to message bus: {}'.format(message_bus_ref.messageBusesId)
    )

    client.Publish(
        message_bus_ref,
        args.json_message,
        args.avro_message,
        args.event_id,
        args.event_type,
        args.event_source,
        args.event_data,
        args.event_attributes,
    )

    return log.out.Print('Event published successfully')
