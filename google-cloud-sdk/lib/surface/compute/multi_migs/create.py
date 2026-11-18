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
"""Command for creating multi-MIGs."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.multi_migs import utils as api_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.multi_migs import utils


DETAILED_HELP = {
    'brief': 'Create a Compute Engine multi-MIG',
    'DESCRIPTION': """\
        *{command}* creates a Compute Engine multi-MIG.
    """,
    'EXAMPLES': """\
      Running:

              $ {command} example-multimig --workload-policy=example-policy

      will create a multi-MIG called 'example-multimig'
      with a workload policy called 'example-policy' in the region and project which were set by `gcloud config set`.

      You can provide full path to multi-MIG name to override the region and
      project or use `--region` and `--project` flags.

      Example:

              $ {command} projects/example-project/regions/us-central1/multiMigs/example-multimig --workload-policy=example-policy --description="Multi-MIG with workload policy"

      will create a multi-MIG called 'example-multimig'
      in the region `us-central1` and project 'example-project' with a
      workload policy called 'projects/example-project/regions/us-central1/resourcePolicies/example-policy' and a description of 'Multi-MIG with workload policy'.
    """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class Create(base.CreateCommand):
  """Create a multi-MIG."""

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    utils.AddMultiMigNameArgToParser(
        parser, base.ReleaseTrack.ALPHA.name.lower()
    )
    parser.add_argument(
        '--description',
        help='Sets description to multi-MIG.',
    )
    parser.add_argument(
        '--workload-policy',
        help='Specifies a workload policy for multi-MIG.',
    )

  def Run(self, args):
    """Creates a multi-MIG.

    Args:
      args: the argparse arguments that this command was invoked with.

    Returns:
      List containing one resource.
    """
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    resources = holder.resources
    multi_mig_ref = args.CONCEPTS.multi_mig.Parse()
    multi_mig = client.messages.MultiMig(
        name=multi_mig_ref.Name(),
        description=args.description,
        region=multi_mig_ref.region,
        resourcePolicies=utils.MakeResourcePolicy(
            args, resources, client.messages, multi_mig_ref
        ),
    )
    return api_utils.Insert(client, multi_mig, multi_mig_ref)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateAlpha(Create):
  """Create a multi-MIG."""

  @classmethod
  def Args(cls, parser):
    utils.AddMultiMigNameArgToParser(
        parser, base.ReleaseTrack.ALPHA.name.lower()
    )
    parser.add_argument(
        '--description',
        help='Sets description to multi-MIG.',
    )
    parser.add_argument(
        '--workload-policy',
        help=(
            'Taking the resource policy ID and specifies a workload policy'
            ' for multi-MIG.'
        ),
    )
