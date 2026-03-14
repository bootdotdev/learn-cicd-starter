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
"""Create resource policy command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.resource_policies import flags
from googlecloudsdk.command_lib.compute.resource_policies import util


def _CommonArgs(parser):
  """A helper function."""

  flags.MakeResourcePolicyArg().AddArgument(parser)
  flags.AddCommonArgs(parser)
  flags.AddTypeArgsForWorkloadPolicy(parser)
  flags.AddMaxTopologyDistanceAndAcceleratorTopologyArgsForWorkloadPolicy(
      parser
  )


def ValidateWorkloadPolicy(resource_policy, messages, args):
  """Validates the workload policy."""
  if args.accelerator_topology is not None and (
      resource_policy.workloadPolicy.type
      != messages.ResourcePolicyWorkloadPolicy.TypeValueValuesEnum.HIGH_THROUGHPUT
  ):
    raise exceptions.InvalidArgumentException(
        '--accelerator-topology',
        'Accelerator topology is only supported for high throughput workload'
        ' policies.',
    )


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class CreateWorkloadPolicyGa(base.CreateCommand):
  """Create a Compute Engine workload resource policy."""

  @staticmethod
  def Args(parser):
    _CommonArgs(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    policy_ref = flags.MakeResourcePolicyArg().ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(holder.client),
    )

    messages = holder.client.messages
    resource_policy = util.MakeWorkloadPolicy(policy_ref, args, messages)
    ValidateWorkloadPolicy(resource_policy, messages, args)
    create_request = messages.ComputeResourcePoliciesInsertRequest(
        resourcePolicy=resource_policy,
        project=policy_ref.project,
        region=policy_ref.region,
    )

    service = holder.client.apitools_client.resourcePolicies
    return client.MakeRequests([(service, 'Insert', create_request)])[0]


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateWorkloadPolicyBeta(CreateWorkloadPolicyGa):
  """Create a Compute Engine workload resource policy."""


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateWorkloadPolicyAlpha(CreateWorkloadPolicyGa):
  """Create a Compute Engine workload resource policy."""


CreateWorkloadPolicyGa.detailed_help = {
    'DESCRIPTION': """Create a Compute Engine workload resource policy.""",
    'EXAMPLES': """\
To create a workload policy:

$ {command} NAME --type=TYPE
"""
}
