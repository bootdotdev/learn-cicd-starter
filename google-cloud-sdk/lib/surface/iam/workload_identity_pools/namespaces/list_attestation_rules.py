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
"""Command to add an attestation rule on a workload identity pool namespace."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import list_pager
from googlecloudsdk.api_lib.iam import util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope.concepts import concepts
from googlecloudsdk.command_lib.util.apis import yaml_data
from googlecloudsdk.command_lib.util.concepts import concept_parsers


@base.Hidden
@base.UniverseCompatible
class ListAttestationRules(base.ListCommand):
  """List the attestation rules on a workload identity pool namespace."""

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
          The following command lists the attestation rules on a workload
          identity pool namespace `my-namespace` with a container id filter.

            $ {command} my-namespace \
            --workload-identity-pool="my-workload-identity-pool" \
            --location="global" \
            --container-id-filter="projects/123,projects/456"
          """,
  }

  @staticmethod
  def Args(parser):
    namespace_data = yaml_data.ResourceYAMLData.FromPath(
        'iam.workload_identity_pool_namespace'
    )
    concept_parsers.ConceptParser.ForResource(
        'namespace',
        concepts.ResourceSpec.FromYaml(
            namespace_data.GetData(), is_positional=True
        ),
        'The namespace to list attestation rules.',
        required=True,
    ).AddToParser(parser)
    parser.add_argument(
        '--container-id-filter',
        help="""Apply a filter on the container ids of the attestation rules
                being listed. Expects a comma-delimited string of project
                numbers in the format `projects/<project-number>,...`.""",
    )
    base.URI_FLAG.RemoveFromParser(parser)

  def Run(self, args):
    client, messages = util.GetClientAndMessages()
    namespace_ref = args.CONCEPTS.namespace.Parse()

    return list_pager.YieldFromList(
        client.projects_locations_workloadIdentityPools_namespaces,
        messages.IamProjectsLocationsWorkloadIdentityPoolsNamespacesListAttestationRulesRequest(
            filter=f'container_ids({ args.container_id_filter})'
            if args.container_id_filter
            else '',
            resource=namespace_ref.RelativeName(),
        ),
        method='ListAttestationRules',
        batch_size=args.page_size,
        limit=args.limit,
        field='attestationRules',
        batch_size_attribute='pageSize',
    )
