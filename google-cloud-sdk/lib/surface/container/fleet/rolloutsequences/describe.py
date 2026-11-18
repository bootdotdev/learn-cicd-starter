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

"""Command to show rollout sequence information."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.container.fleet import client
from googlecloudsdk.api_lib.container.fleet import util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import parser_arguments
from googlecloudsdk.command_lib.container.fleet.rolloutsequences import flags as rolloutsequence_flags
from googlecloudsdk.generated_clients.apis.gkehub.v1alpha import gkehub_v1alpha_messages as alpha_messages

_EXAMPLES = """
To describe a rollout sequence named `my-rollout-sequence`,
run:

$ {command} my-rollout-sequence
"""


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Describe(base.DescribeCommand):
  """Describe a rollout sequence."""

  detailed_help = {'EXAMPLES': _EXAMPLES}

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor):
    flags = rolloutsequence_flags.RolloutSequenceFlags(parser)
    flags.AddRolloutSequenceResourceArg()

  def Run(self, args):
    req = alpha_messages.GkehubProjectsLocationsRolloutSequencesGetRequest(
        name=util.RolloutSequenceName(args)
    )

    fleet_client = client.FleetClient(release_track=base.ReleaseTrack.ALPHA)
    return fleet_client.DescribeRolloutSequence(req)
