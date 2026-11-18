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
"""Command to delete the specified message bus."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.eventarc import message_buses
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.eventarc import flags
from googlecloudsdk.core.console import console_io

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To delete the message bus `my-message-bus` in location `us-central1`, run:

          $ {command} my-message-bus --location=us-central1
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Delete(base.DeleteCommand):
  """Delete an Eventarc message bus."""

  detailed_help = _DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    flags.AddMessageBusResourceArg(
        parser, 'Message bus to delete.', required=True
    )
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run the delete command."""
    client = message_buses.MessageBusClientV1()
    message_bus_ref = args.CONCEPTS.message_bus.Parse()

    console_io.PromptContinue(
        message=(
            'The following message bus will be deleted.\n'
            '[{name}] in location [{location}]'.format(
                name=message_bus_ref.messageBusesId,
                location=message_bus_ref.locationsId,
            )
        ),
        throw_if_unattended=True,
        cancel_on_no=True,
    )
    operation = client.Delete(message_bus_ref)

    if args.async_:
      return operation
    return client.WaitFor(operation, 'Deleting', message_bus_ref)
