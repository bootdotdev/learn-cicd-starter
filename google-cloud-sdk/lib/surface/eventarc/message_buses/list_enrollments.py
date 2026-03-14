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
"""Command to list all message buses in a project and location."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.eventarc import enrollments
from googlecloudsdk.api_lib.eventarc import message_buses
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.eventarc import flags

_DETAILED_HELP = {
    "DESCRIPTION": "{description}",
    "EXAMPLES": """\
        To list all enrollments in message-bus `my-message-bus` in `us-central1`, run:

          $ {command} my-message-bus --location=us-central1
        """,
}

_FORMAT = """ \
table(
    list().scope("projects").segment(1):label=ENROLLMENT_PROJECT,
    list().scope("enrollments"):label=NAME
)
"""


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class ListEnrollments(base.ListCommand):
  """List Eventarc enrollments attached to an Eventarc message bus."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    flags.AddMessageBusResourceArg(
        parser, "The message bus on which to list enrollments.", required=True
    )
    parser.display_info.AddFormat(_FORMAT)
    parser.display_info.AddUriFunc(enrollments.GetEnrollmentURI)

  def Run(self, args):
    client = message_buses.MessageBusClientV1()
    message_bus_ref = args.CONCEPTS.message_bus.Parse()
    return client.ListEnrollments(message_bus_ref, args.limit, args.page_size)
