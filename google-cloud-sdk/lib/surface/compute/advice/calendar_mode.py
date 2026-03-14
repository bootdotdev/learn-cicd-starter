# -*- coding: utf-8 -*- #
# Copyright 2025 Google LLC. All Rights Reserved.
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

"""Command for advicing best zone and window time for future reservations."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.advice import flags
from googlecloudsdk.command_lib.compute.advice import util


DETAILED_HELP = {
    'DESCRIPTION': """
      Recommends the optimal time window and zone for Future Reservations.
    """,
    'EXAMPLES': """
      To request an advice for a future reservation of 8 a3-highgpu-8g VMs, run:

      $ {command}
        --region=fake-region
        --machine-type=a3-megagpu-8g
        --vm-count=8
        --duration-range=min=7d,max=14d
        --start-time-range=from=2025-02-20,to=2025-03-25
        --end-time-range=from=2025-02-20,to=2025-03-25

      To request advice for a future reservation of 512 v5e TPUs, run:

        $ {command}
          --region=fake-region
          --location-policy=fake-zone-1=DENY,fake-zone-2=ALLOW
          --tpu-version=V5E
          --chip-count=16
          --workload-type=BATCH
          --duration-range=min=30d,max=90d
          --start-time-range=from=2025-02-25,to=2025-06-25
          --end-time-range=from=2025-02-25,to=2025-06-25
    """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CalendarMode(base_classes.BaseCommand):
  """Recommends the optimal time window and zone for Future Reservations."""

  detailed_help = DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    """Adds arguments for the calendar-mode command to a parser."""
    flags.AddRegionFlag(parser)
    flags.AddLocationPolicyFlag(parser)
    flags.AddStartTimeRangeFlag(parser)
    flags.AddEndTimeRangeFlag(parser)
    flags.AddDurationRangeFlag(parser)
    flags.AddAcceleratorPropertiesFlags(parser)
    flags.AddDeploymentTypeFlag(parser)

  def Run(self, args):
    """Runs the calendar-mode command."""

    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = client.messages

    # Construct the Request message using the arguments.
    request_message = util.GetComputeAdviceCalendarModeRequest(args, messages)

    # Call the API and return the response.
    service = client.apitools_client.advice
    method_name = 'CalendarMode'
    return client.MakeRequests([(service, method_name, request_message)])


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CalendarModeAlpha(CalendarMode):
  """Recommends the optimal time window and zone for Future Reservations."""

  detailed_help = DETAILED_HELP

