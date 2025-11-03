# -*- coding: utf-8 -*- #
# Copyright 2025 Google Inc. All Rights Reserved.
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
"""services mcp content-security add command."""

from googlecloudsdk.api_lib.services import services_util
from googlecloudsdk.api_lib.services import serviceusage
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.services import common_flags
from googlecloudsdk.core import properties

_PROJECT_RESOURCE = 'projects/%s'
_CONTENT_SECURITY_POLICY_DEFAULT = '/contentSecurityPolicies/%s'


# TODO(b/321801975) make command public after suv2 launch.
@base.UniverseCompatible
@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Add(base.Command):
  """Add MCP content security provider of a project.

  Add MCP content security provider of a project.

  ## EXAMPLES

  Add MCP content security provider  of a project:

    $ {command} my-mcp-content-security-provider

  Add MCP content security provider of a project `my-project`:

    $ {command} my-mcp-content-security-provider --project=my-project
  """

  @staticmethod
  def Args(parser):
    common_flags.mcp_content_security_provider_flag(
        suffix='to add'
    ).AddToParser(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      The content security providers for a project.
    """

    if args.IsSpecified('project'):
      resource_name = _PROJECT_RESOURCE % args.project
    else:
      project = properties.VALUES.core.project.Get(required=True)
      resource_name = _PROJECT_RESOURCE % project

    op = serviceusage.AddContentSecurityProvider(
        args.mcp_content_security_provider,
        resource_name + _CONTENT_SECURITY_POLICY_DEFAULT % 'default',
    )
    op = services_util.WaitOperation(op.name, serviceusage.GetOperationV2Beta)
    services_util.PrintOperation(op)
