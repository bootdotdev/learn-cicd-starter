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
"""Update Instance schedule policy command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.resource_policies import flags
from googlecloudsdk.command_lib.compute.resource_policies import util


def _CommonArgs(parser):
  """A helper function to build args."""
  flags.MakeResourcePolicyArg().AddArgument(parser)
  flags.AddCommonArgs(parser)
  flags.AddInstanceScheduleArgs(parser)


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class UpdateInstanceSchedule(base.UpdateCommand):
  """Update a Compute Engine Instance Schedule Resource Policy."""

  @staticmethod
  def Args(parser):
    _CommonArgs(parser)

  def Run(self, args):
    return self._Run(args)

  def _Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = holder.client.messages
    policy_ref = flags.MakeResourcePolicyArg().ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(holder.client),
    )

    resource_policy = util.MakeInstanceSchedulePolicyForUpdate(
        policy_ref, args, messages
    )

    patch_request = messages.ComputeResourcePoliciesPatchRequest(
        resourcePolicy=policy_ref.Name(),
        resourcePolicyResource=resource_policy,
        project=policy_ref.project,
        region=policy_ref.region,
    )
    service = holder.client.apitools_client.resourcePolicies
    return client.MakeRequests([(service, 'Patch', patch_request)])


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.DefaultUniverseOnly
class UpdateInstanceScheduleBeta(UpdateInstanceSchedule):
  """Update a Compute Engine Instance Schedule Resource Policy."""

  @staticmethod
  def Args(parser):
    _CommonArgs(parser)

  def Run(self, args):
    return self._Run(args)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class UpdateInstanceScheduleAlpha(UpdateInstanceSchedule):
  """Update a Compute Engine Instance Schedule Resource Policy."""

  @staticmethod
  def Args(parser):
    _CommonArgs(parser)

  def Run(self, args):
    return self._Run(args)


UpdateInstanceSchedule.detailed_help = {
    'DESCRIPTION': """\
Update a Compute Engine Instance Schedule Resource Policy.
""",
    'EXAMPLES': """\
To update an instance schedule resource policy with specified parameters:

  $ {command} NAME \
    --region=REGION
    --timezone=UTC \
    --vm-start-schedule="0 7 * * *" \
    --vm-stop-schedule="0 17 * * *"
""",
}
