# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
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
"""Command to resume a fleet rollout."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from typing import Any

from apitools.base.py import encoding

from googlecloudsdk import core
from googlecloudsdk.api_lib.container.fleet import client
from googlecloudsdk.api_lib.container.fleet import util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import parser_arguments
from googlecloudsdk.calliope import parser_extensions
from googlecloudsdk.command_lib.container.fleet.rollouts import flags as rollout_flags
from googlecloudsdk.generated_clients.apis.gkehub.v1alpha import gkehub_v1alpha_messages as alpha_messages

_EXAMPLES = """
To resume a rollout, run:

$ {command} ROLLOUT
"""


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Resume(base.UpdateCommand):
  """Resume a rollout resource."""

  detailed_help = {'EXAMPLES': _EXAMPLES}

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor):
    """Registers flags for the resume command."""
    flags = rollout_flags.RolloutFlags(parser)
    flags.AddRolloutResourceArg()
    flags.AddScheduleOffset()
    flags.AddValidateOnly()
    flags.AddAsync()

  def Run(self, args: parser_extensions.Namespace) -> alpha_messages.Operation:
    """Runs the resume command."""
    flag_parser = rollout_flags.RolloutFlagParser(
        args, release_track=base.ReleaseTrack.ALPHA
    )
    fleet_client = client.FleetClient(release_track=self.ReleaseTrack())
    operation_client = client.OperationClient(
        release_track=base.ReleaseTrack.ALPHA
    )
    rollout_ref = util.RolloutRef(args)
    utils = _Utils(args, operation_client, fleet_client)

    if flag_parser.Async():
      # This effectively skips the confirmation prompt when resuming with an
      # offset.
      operation = utils.resume_rollout_async(
          flag_parser.ScheduleOffset(),
          flag_parser.ValidateOnly()
      )
      core.log.Print(
          'Resume in progress for Fleet rollout [{}]'.format(
              rollout_ref.SelfLink()
          )
      )
      return operation

    if flag_parser.ValidateOnly():
      completed_operation = utils.resume_rollout_sync(
          flag_parser.ScheduleOffset(), True)
      utils.log_schedule(completed_operation, rollout_ref)
    elif flag_parser.ScheduleOffset():
      # This is not a transaction - the rollout could theoretically be resumed
      # with a different schedule than that displayed to the user, if a
      # concurrent resume is invoked before the user confirms.
      completed_operation = utils.resume_rollout_sync(
          flag_parser.ScheduleOffset(), True
      )
      utils.log_schedule(completed_operation, rollout_ref)

      core.console.console_io.PromptContinue(
          message=(
              'Do you want to resume the rollout with the displayed schedule?'
          ),
          throw_if_unattended=True,
          cancel_on_no=True,
      )
      completed_operation = utils.resume_rollout_sync(
          flag_parser.ScheduleOffset(), False
      )
      core.log.Print(
          'Resumed Fleet rollout [{}].'.format(rollout_ref.SelfLink())
      )
    else:
      completed_operation = utils.resume_rollout_sync(
          flag_parser.ScheduleOffset(), flag_parser.ValidateOnly()
      )
      core.log.Print(
          'Resumed Fleet rollout [{}].'.format(rollout_ref.SelfLink())
      )

    return completed_operation


class _Utils:
  """Utility functions for the resume command."""

  def __init__(
      self,
      args,
      operation_client: client.OperationClient,
      fleet_client: client.FleetClient
  ):
    self.rollout_name = util.RolloutName(args)
    self.operation_client = operation_client
    self.fleet_client = fleet_client

  def resume_rollout_async(self, offset: str, validate_only: bool) -> Any:
    req = alpha_messages.GkehubProjectsLocationsRolloutsResumeRequest()
    req.name = self.rollout_name
    req.resumeRolloutRequest = alpha_messages.ResumeRolloutRequest(
        scheduleOffset=offset,
        validateOnly=validate_only,
    )
    return self.fleet_client.ResumeRollout(req)

  def resume_rollout_sync(self, offset: str, validate_only: bool) -> Any:
    operation = self.resume_rollout_async(offset, validate_only)
    return self.operation_client.Wait(util.OperationRef(operation))

  @staticmethod
  def log_schedule(
      completed_operation: Any, rollout_ref: core.resources.Resource
  ) -> None:
    """Pretty prints the returned rollout schedule."""
    resp = encoding.MessageToDict(completed_operation)
    core.log.Print(
        'Schedule after resume for fleet rollout [{}]:'.format(
            rollout_ref.SelfLink()
        )
    )

    waves = {
        wave['waveNumber']: (wave['waveStartTime'], wave['waveEndTime'])
        for wave in resp['schedule']['waves']
    }
    for n in range(1, len(waves) + 1):
      core.log.Print('Wave {}: [{}, {}]'.format(n, waves[n][0], waves[n][1]))
