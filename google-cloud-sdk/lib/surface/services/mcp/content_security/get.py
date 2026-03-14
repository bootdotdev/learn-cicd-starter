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
"""services mcp content-security get command."""

import collections

from googlecloudsdk.api_lib.services import serviceusage
from googlecloudsdk.calliope import base
from googlecloudsdk.core import properties

_PROJECT_RESOURCE = 'projects/%s'
_MCP_POLICY_DEFAULT = '/mcpPolicies/default'


# TODO(b/321801975) make command public after suv2 launch.
@base.UniverseCompatible
@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Get(base.Command):
  """Get content security providers from MCP policy of a project.

  Get content security providers from MCP policy of a project.

  ## EXAMPLES

  Get content security providers from MCP policy of a project:

    $ {command}

  Get content security providers from MCP policy of a project `my-project`:

    $ {command} --project=my-project
  """

  @staticmethod
  def Args(parser):
    parser.display_info.AddFormat("""
          table(
            contentSecurityProvider
          )
        """)

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

    content_security = serviceusage.GetMcpPolicy(
        resource_name + _MCP_POLICY_DEFAULT,
    ).contentSecurity

    content_security_providers = []
    results = collections.namedtuple(
        'ContentSecurityProvider', ['contentSecurityProvider']
    )

    for content_security_provider in content_security.contentSecurityProviders:
      content_security_providers.append(results(content_security_provider.name))

    return content_security_providers
