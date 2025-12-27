# -*- coding: utf-8 -*- #
# Copyright 2024 Google Inc. All Rights Reserved.
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
"""Command for getting effective security policies of backend services."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import firewalls_utils
from googlecloudsdk.api_lib.compute import lister
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.backend_services import flags
from googlecloudsdk.core import log


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class GetEffectiveSecurityPolicies(base.DescribeCommand, base.ListCommand):
  """Get the effective security policies of a Compute Engine backend service.

  *{command}* is used to get the effective security policies applied to the
  backend service.

  ## EXAMPLES

  To get the effective security policies for a backend service, run:

    $ {command} example-backend-service

  gets the effective security policies applied on the backend service
  'example-backend-service'.
  """

  @staticmethod
  def Args(parser):
    flags.GLOBAL_BACKEND_SERVICE_ARG.AddArgument(
        parser, operation_type='get effective security policies'
    )
    parser.display_info.AddFormat(
        firewalls_utils.EFFECTIVE_SECURITY_POLICY_LIST_FORMAT
    )
    lister.AddBaseListerArgs(parser)

  def _GetSecurityPolicyName(self, sp_ref):
    sp_ref_list = sp_ref.split('/')
    return sp_ref_list[-1]

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    backend_service_ref = flags.GLOBAL_BACKEND_SERVICE_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
    )
    get_request = client.messages.ComputeBackendServicesGetRequest(
        **backend_service_ref.AsDict()
    )
    get_response = client.MakeRequests([
        (client.apitools_client.backendServices, 'Get', get_request),
    ])[0]

    has_edge_sp = False
    has_sp = False
    get_effective_sp_request = client.messages.ComputeBackendServicesGetEffectiveSecurityPoliciesRequest(
        **backend_service_ref.AsDict()
    )
    requests = [(
        client.apitools_client.backendServices,
        'GetEffectiveSecurityPolicies',
        get_effective_sp_request,
    )]
    if (
        hasattr(get_response, 'edgeSecurityPolicy')
        and get_response.edgeSecurityPolicy
    ):
      get_edge_sp_request = client.messages.ComputeSecurityPoliciesGetRequest(
          project=backend_service_ref.project,
          securityPolicy=self._GetSecurityPolicyName(
              get_response.edgeSecurityPolicy
          ),
      )
      requests.append((
          client.apitools_client.securityPolicies,
          'Get',
          get_edge_sp_request,
      ))
      has_edge_sp = True
    if hasattr(get_response, 'securityPolicy') and get_response.securityPolicy:
      get_sp_request = client.messages.ComputeSecurityPoliciesGetRequest(
          project=backend_service_ref.project,
          securityPolicy=self._GetSecurityPolicyName(
              get_response.securityPolicy
          ),
      )
      requests.append((
          client.apitools_client.securityPolicies,
          'Get',
          get_sp_request,
      ))
      has_sp = True

    responses = client.MakeRequests(requests)
    get_effective_sp_response = responses[0]
    org_policies = []
    edge_policy = None
    backend_policy = None
    all_policies = []

    if hasattr(get_effective_sp_response, 'securityPolicies'):
      org_policies.extend(get_effective_sp_response.securityPolicies)
    if has_edge_sp:
      edge_policy = responses[1]
      if has_sp:
        backend_policy = responses[2]
    elif has_sp:
      backend_policy = responses[1]

    all_policies.extend(org_policies)
    if edge_policy:
      all_policies.append(edge_policy)
    if backend_policy:
      all_policies.append(backend_policy)

    if args.IsSpecified('format') and args.format == 'json':
      return (
          client.messages.BackendServicesGetEffectiveSecurityPoliciesResponse(
              securityPolicies=all_policies
          )
      )

    result = []
    for sp in org_policies:
      result.extend(
          firewalls_utils.ConvertOrgSecurityPolicyRulesToEffectiveSpRules(sp)
      )
    if edge_policy:
      result.extend(
          firewalls_utils.ConvertSecurityPolicyRulesToEffectiveSpRules(
              edge_policy
          )
      )
    if backend_policy:
      result.extend(
          firewalls_utils.ConvertSecurityPolicyRulesToEffectiveSpRules(
              backend_policy
          )
      )
    return result

  def Epilog(self, resources_were_displayed):
    del resources_were_displayed
    log.status.Print('\n' + firewalls_utils.LIST_NOTICE_SECURITY_POLICY)


GetEffectiveSecurityPolicies.detailed_help = {
    'EXAMPLES': """\
    To get the effective security policies of backend_service with name
    example-backend_service, run:

      $ {command} example-backend_service

    To show all fields of the security policy, please show in JSON format with
    option --format=json

    To list more the fields of the effective security policy rules in table
    format, run:

      $ {command} example-backend_service --format="table(
        type,
        security_policy_name,
        priority,
        description,
        action,
        preview,
        expression,
        src_ip_ranges.list():label=SRC_RANGES)"
        """,
}
