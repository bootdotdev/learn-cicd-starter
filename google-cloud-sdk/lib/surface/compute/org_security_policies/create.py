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
"""Command for creating organization security policies."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.org_security_policies import client
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute.org_security_policies import flags
from googlecloudsdk.command_lib.compute.security_policies import security_policies_utils
from googlecloudsdk.core.util import files
import six


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Create(base.CreateCommand):
  """Create a Compute Engine organization security policy.

  *{command}* is used to create organization security policies. An organization
  security policy is a set of rules that controls access to various resources.
  """

  ORG_SECURITY_POLICY_ARG = None

  @classmethod
  def Args(cls, parser):
    flags.AddArgSpCreation(parser)
    parser.display_info.AddCacheUpdater(flags.OrgSecurityPoliciesCompleter)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    org_security_policy = client.OrgSecurityPolicy(
        compute_client=holder.client,
        resources=holder.resources,
        version=six.text_type(self.ReleaseTrack()).lower())

    if args.IsSpecified('organization'):
      parent_id = 'organizations/' + args.organization
    elif args.IsSpecified('folder'):
      parent_id = 'folders/' + args.folder

    if args.IsSpecified('file_name'):
      security_policy = self._GetTemplateFromFile(args, holder.client.messages)
    else:
      if args.IsSpecified('type') and args.type == 'CLOUD_ARMOR':
        security_policy = holder.client.messages.SecurityPolicy(
            description=args.description,
            shortName=args.short_name,
            type=(
                holder.client.messages.SecurityPolicy.TypeValueValuesEnum.CLOUD_ARMOR
            ),
        )
      else:
        security_policy = holder.client.messages.SecurityPolicy(
            description=args.description,
            displayName=args.display_name,
            type=(
                holder.client.messages.SecurityPolicy.TypeValueValuesEnum.FIREWALL
            ),
        )

    return org_security_policy.Create(
        security_policy=security_policy,
        parent_id=parent_id,
        only_generate_request=False)

  def _GetTemplateFromFile(self, args, messages):
    if not os.path.exists(args.file_name):
      raise exceptions.BadFileException(
          'No such file [{0}]'.format(args.file_name)
      )
    if os.path.isdir(args.file_name):
      raise exceptions.BadFileException(
          '[{0}] is a directory'.format(args.file_name)
      )
    try:
      with files.FileReader(args.file_name) as import_file:
        if args.file_format == 'json':
          return security_policies_utils.SecurityPolicyFromFile(
              import_file, messages, 'json'
          )
        return security_policies_utils.SecurityPolicyFromFile(
            import_file, messages, 'yaml'
        )
    except Exception as exp:
      exp_msg = getattr(exp, 'message', six.text_type(exp))
      msg = (
          'Unable to read security policy config from specified file '
          '[{0}] because [{1}]'.format(args.file_name, exp_msg)
      )
      raise exceptions.BadFileException(msg)


Create.detailed_help = {
    'EXAMPLES': """\
    To create an organization security policy under folder with ID ``123456789'',
    run:

      $ {command} --short-name=my-policy --folder=123456789

    To create an organization security under organization with ID ``12345'' from
    an input file, run:

      $ {command} --file-name=my-file-name --organization=12345
    """,
}
