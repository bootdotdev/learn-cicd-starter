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
"""Command to set attestation rules on a workload identity pool namespace."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import encoding
from googlecloudsdk.api_lib.iam import util
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as gcloud_exceptions
from googlecloudsdk.calliope.concepts import concepts
from googlecloudsdk.command_lib.iam import identity_pool_waiter
from googlecloudsdk.command_lib.util.apis import yaml_data
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.core import log
from googlecloudsdk.core import resources as sdkresources
from googlecloudsdk.core import yaml
import six


@base.Hidden
@base.UniverseCompatible
class AddAttestationRule(base.Command):
  """Set attestation rules on a workload identity pool namespace."""

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
          The following command sets attestation rules on a workload identity
          pool namespace `my-namespace` using a policy file.

            $ {command} my-namespace \
            --workload-identity-pool="my-workload-identity-pool" \
            --location="global" \
            --policy-file="policy.json"
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
        'The workload identity pool namespace to set attestations rule on.',
        required=True,
    ).AddToParser(parser)
    parser.add_argument(
        '--policy-file',
        help="""\
          Path to a local JSON-formatted or YAML-formatted file containing an
          attestation policy, structured as a [list of attestation rules](https://cloud.google.com/iam/docs/reference/rest/v1/projects.locations.workloadIdentityPools.namespaces/setAttestationRules#request-body).
          """,
        required=True,
    )
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    client, messages = util.GetClientAndMessages()
    namespace_ref = args.CONCEPTS.namespace.Parse()

    policy_to_parse = yaml.load_path(args.policy_file)

    try:
      set_attestation_rules_request = encoding.PyValueToMessage(
          messages.SetAttestationRulesRequest, policy_to_parse
      )
    except AttributeError as e:
      # Raised when the input file is not properly formatted YAML policy file.
      raise gcloud_exceptions.BadFileException(
          'Policy file [{0}] is not a properly formatted YAML or JSON '
          'policy file. {1}'.format(args.policy_file, six.text_type(e))
      )

    lro_ref = client.projects_locations_workloadIdentityPools_namespaces.SetAttestationRules(
        messages.IamProjectsLocationsWorkloadIdentityPoolsNamespacesSetAttestationRulesRequest(
            resource=namespace_ref.RelativeName(),
            setAttestationRulesRequest=set_attestation_rules_request,
        )
    )

    log.status.Print(
        'Set attestation rules request issued for: [{}]'.format(
            namespace_ref.namespacesId
        )
    )

    if args.async_:
      return lro_ref

    result = waiter.WaitFor(
        poller=identity_pool_waiter.IdentityPoolOperationPollerNoResources(
            client.projects_locations_workloadIdentityPools_namespaces,
            client.projects_locations_workloadIdentityPools_namespaces_operations,
        ),
        operation_ref=sdkresources.REGISTRY.ParseRelativeName(
            lro_ref.name,
            collection=(
                'iam.projects.locations.workloadIdentityPools.namespaces.operations'
            ),
        ),
        message='Waiting for operation [{}] to complete'.format(lro_ref.name),
        # Wait for a maximum of 5 minutes, as the IAM replication has a lag of
        # up to 80 seconds.
        max_wait_ms=300000,
    )

    log.status.Print(
        'Set attestation rules for [{}].'.format(namespace_ref.namespacesId)
    )

    return result
