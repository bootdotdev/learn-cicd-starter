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
"""Command to delete a rollout sequence."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from googlecloudsdk.api_lib.container.fleet import client
from googlecloudsdk.api_lib.container.fleet import util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import parser_arguments
from googlecloudsdk.calliope import parser_extensions
from googlecloudsdk.command_lib.container.fleet.rolloutsequences import flags as rolloutsequence_flags
from googlecloudsdk.core import log
from googlecloudsdk.generated_clients.apis.gkehub.v1alpha import gkehub_v1alpha_messages as alpha_messages


_EXAMPLES = """
To delete a rollout sequence, run:

$ {command} ROLLOUTSEQUENCE
"""


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Delete(base.DeleteCommand):
  """Delete a rollout sequence resource."""

  detailed_help = {'EXAMPLES': _EXAMPLES}

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor):
    """Registers flags for the delete command."""
    flags = rolloutsequence_flags.RolloutSequenceFlags(parser)
    flags.AddRolloutSequenceResourceArg()
    flags.AddAsync()

  def Run(self, args: parser_extensions.Namespace) -> alpha_messages.Operation:
    """Runs the delete command."""
    flag_parser = rolloutsequence_flags.RolloutSequenceFlagParser(
        args, release_track=base.ReleaseTrack.ALPHA
    )
    req = alpha_messages.GkehubProjectsLocationsRolloutSequencesDeleteRequest()
    req.name = util.RolloutSequenceName(args)

    fleet_client = client.FleetClient(release_track=self.ReleaseTrack())
    operation = fleet_client.DeleteRolloutSequence(req)
    rolloutsequence_ref = util.RolloutSequenceRef(args)

    if flag_parser.Async():
      log.Print(
          'Delete in progress for Rollout sequence [{}]'.format(
              rolloutsequence_ref.SelfLink()
          )
      )
      return operation

    operation_client = client.OperationClient(
        release_track=base.ReleaseTrack.ALPHA
    )
    completed_operation = operation_client.Wait(util.OperationRef(operation))
    log.Print(
        'Deleted Rollout sequence [{}].'.format(
            rolloutsequence_ref.SelfLink()
        )
    )

    return completed_operation
