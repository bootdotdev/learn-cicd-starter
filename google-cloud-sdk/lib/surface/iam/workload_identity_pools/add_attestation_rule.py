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
"""Command to add an attestation rule on a workload identity pool."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.iam import util
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope.concepts import concepts
from googlecloudsdk.command_lib.iam import identity_pool_waiter
from googlecloudsdk.command_lib.util.apis import yaml_data
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.core import log
from googlecloudsdk.core import resources as sdkresources


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.Hidden
class AddAttestationRule(base.Command):
  """Add an attestation rule on a workload identity pool."""

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
          The following command adds an attestation rule with a Google Cloud
          resource on a workload identity pool `my-pool`.

            $ {command} my-pool \
            --location="global" \
            --google-cloud-resource="//run.googleapis.com/projects/123/type/Service/*"
          """,
  }

  @staticmethod
  def Args(parser):
    workload_pool_data = yaml_data.ResourceYAMLData.FromPath(
        'iam.workload_identity_pool'
    )
    concept_parsers.ConceptParser.ForResource(
        'workload_identity_pool',
        concepts.ResourceSpec.FromYaml(
            workload_pool_data.GetData(), is_positional=True
        ),
        'The workload identity pool to add the attestation rule on.',
        required=True,
    ).AddToParser(parser)
    parser.add_argument(
        '--google-cloud-resource',
        help="""A single workload running on Google Cloud. This will be set
                in the attestation rule to be added.""",
        required=True,
    )
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    client, messages = util.GetClientAndMessages()
    workload_pool_ref = args.CONCEPTS.workload_identity_pool.Parse()

    add_attestation_rule_request = messages.AddAttestationRuleRequest(
        attestationRule=messages.AttestationRule(
            googleCloudResource=args.google_cloud_resource,
        )
    )

    lro_ref = client.projects_locations_workloadIdentityPools.AddAttestationRule(
        messages.IamProjectsLocationsWorkloadIdentityPoolsAddAttestationRuleRequest(
            resource=workload_pool_ref.RelativeName(),
            addAttestationRuleRequest=add_attestation_rule_request,
        )
    )

    log.status.Print(
        'Add attestation rule request issued for: [{}]'.format(
            workload_pool_ref.workloadIdentityPoolsId
        )
    )

    if args.async_:
      return lro_ref

    result = waiter.WaitFor(
        poller=identity_pool_waiter.IdentityPoolOperationPollerNoResources(
            client.projects_locations_workloadIdentityPools,
            client.projects_locations_workloadIdentityPools_operations,
        ),
        operation_ref=sdkresources.REGISTRY.ParseRelativeName(
            lro_ref.name,
            collection=(
                'iam.projects.locations.workloadIdentityPools.operations'
            ),
        ),
        message='Waiting for operation [{}] to complete'.format(lro_ref.name),
        # Wait for a maximum of 5 minutes, as the IAM replication has a lag of
        # up to 80 seconds.
        max_wait_ms=300000,
    )

    log.status.Print(
        'Added attestation rule for [{}].'.format(
            workload_pool_ref.workloadIdentityPoolsId
        )
    )

    return result
