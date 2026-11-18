# -*- coding: utf-8 -*- #
# Copyright 2019 Google Inc. All Rights Reserved.
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
"""Command for updating organization security policies."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.org_security_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.org_security_policies import flags
from googlecloudsdk.command_lib.compute.org_security_policies import org_security_policies_utils
from googlecloudsdk.command_lib.compute.security_policies import flags as sp_flags
from googlecloudsdk.command_lib.compute.security_policies import security_policies_utils
import six


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Update(base.UpdateCommand):
  """Update a Compute Engine organization security policy.

  *{command}* is used to update organization security policies. An organization
  security policy is a set of rules that controls access to various resources.
  """

  ORG_SECURITY_POLICY_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.ORG_SECURITY_POLICY_ARG = flags.OrgSecurityPolicyArgument(
        required=True, operation='update')
    cls.ORG_SECURITY_POLICY_ARG.AddArgument(parser, operation_type='update')
    flags.AddArgsUpdateSp(parser)
    sp_flags.AddAdvancedOptions(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.ORG_SECURITY_POLICY_ARG.ResolveAsResource(
        args, holder.resources, with_project=False)
    org_security_policy = client.OrgSecurityPolicy(
        ref=ref,
        compute_client=holder.client,
        resources=holder.resources,
        version=six.text_type(self.ReleaseTrack()).lower())
    sp_id = org_security_policies_utils.GetSecurityPolicyId(
        org_security_policy, ref.Name(), organization=args.organization)
    existing_security_policy = org_security_policy.Describe(
        sp_id=sp_id, only_generate_request=False)[0]
    description = existing_security_policy.description
    advanced_options_config = existing_security_policy.advancedOptionsConfig
    if args.description is not None:
      description = args.description
    if (args.IsSpecified('json_parsing') or
        args.IsSpecified('json_custom_content_types') or
        args.IsSpecified('log_level') or
        args.IsSpecified('user_ip_request_headers')):
      advanced_options_config = (
          security_policies_utils.CreateAdvancedOptionsConfig(
              holder.client, args, advanced_options_config))
    security_policy = holder.client.messages.SecurityPolicy(
        description=description,
        advancedOptionsConfig=advanced_options_config,
        fingerprint=existing_security_policy.fingerprint)

    return org_security_policy.Update(
        sp_id=sp_id,
        only_generate_request=False,
        security_policy=security_policy)


Update.detailed_help = {
    'EXAMPLES':
        """\
    To update an organization security policy with ID ``123456789'' to change the
    description to ``New description'', run:

      $ {command} 123456789 --description='New description'
    """,
}
