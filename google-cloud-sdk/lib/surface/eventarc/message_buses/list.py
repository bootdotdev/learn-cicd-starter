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

from googlecloudsdk.api_lib.eventarc import message_buses
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.eventarc import flags

_DETAILED_HELP = {
    "DESCRIPTION": "{description}",
    "EXAMPLES": """\
        To list all message buses in location ``us-central1'', run:

          $ {command} --location=us-central1

        To list all message buses in all locations, run:

          $ {command} --location=-

        or

          $ {command}
        """,
}

_FORMAT = """\
table(
    name.scope("messageBuses"):label=NAME,
    name.scope("locations").segment(0):label=LOCATION,
    loggingConfig.logSeverity:label=LOGGING_CONFIG
)
"""


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class List(base.ListCommand):
  """List Eventarc message buses."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    flags.AddLocationResourceArg(
        parser,
        "The location for which to list message buses. This should be one of"
        " the supported regions.",
        required=False,
        allow_aggregation=True,
    )
    flags.AddProjectResourceArg(parser)
    parser.display_info.AddFormat(_FORMAT)
    parser.display_info.AddUriFunc(message_buses.GetMessageBusURI)

  def Run(self, args):
    client = message_buses.MessageBusClientV1()
    location_ref = args.CONCEPTS.location.Parse()
    return client.List(location_ref, args.limit, args.page_size)
