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

"""services mcp enable command."""

from googlecloudsdk.api_lib.services import services_util
from googlecloudsdk.api_lib.services import serviceusage
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.services import common_flags
from googlecloudsdk.core import log
from googlecloudsdk.core import properties

_OP_BASE_CMD = 'gcloud beta services operations '
_OP_WAIT_CMD = _OP_BASE_CMD + 'wait {0}'

_SERVICE = 'services/%s'
_PROJECT_RESOURCE = 'projects/{}'
_FOLDER_RESOURCE = 'folders/{}'
_ORGANIZATION_RESOURCE = 'organizations/{}'
_CONSUMER_POLICY_DEFAULT = '/consumerPolicies/{}'


# TODO(b/321801975) make command public after preview.
@base.UniverseCompatible
@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Enable(base.SilentCommand):
  """Enables a service for MCP on a project, folder or organization.

  Enables a service for MCP on a project, folder or organization

  ## EXAMPLES

  To enable a service for MCP called `my-service` on the current project, run:

    $ {command} my-service

  To enable a service for MCP called `my-service` on the project
  `my-project`, run:

    $ {command} my-service --project=my-project

  To enable a service for MCP called `my-service` on the folder
  `my-folder, run:

    $ {command} my-service --folder=my-folder

  To enable a service for MCP called `my-service` on the organization
  `my-organization`, run:

    $ {command} my-service --organization=my-organization

  To run the same command asynchronously (non-blocking), run:

    $ {command} my-service --async
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    common_flags.service_flag(suffix='to enable MCP').AddToParser(parser)
    common_flags.add_resource_args(parser)
    common_flags.skip_mcp_endpoint_check_flag(parser)

    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run 'services mcp enable'.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      Updated MCP Policy.
    """
    if args.IsSpecified('folder'):
      resource_name = _FOLDER_RESOURCE.format(args.folder)
    elif args.IsSpecified('organization'):
      resource_name = _ORGANIZATION_RESOURCE.format(args.organization)
    elif args.IsSpecified('project'):
      resource_name = _PROJECT_RESOURCE.format(args.project)
    else:
      project = properties.VALUES.core.project.Get(required=True)
      resource_name = _PROJECT_RESOURCE.format(project)

    project = (
        args.project
        if args.IsSpecified('project')
        else properties.VALUES.core.project.Get(required=True)
    )
    folder = args.folder if args.IsSpecified('folder') else None
    organization = (
        args.organization if args.IsSpecified('organization') else None
    )

    # check if sevice has Mcp Config
    service_metadata = serviceusage.GetServiceV2Beta(
        f'{resource_name}/services/{args.service}'
    )
    if not args.skip_mcp_endpoint_check and (
        not service_metadata.service.mcpServer
        or not service_metadata.service.mcpServer.urls
    ):
      log.error(
          f'The {args.service} does not have MCP endpoint. You can use'
          ' --skip-mcp-endpoint-check to bypass this check.'
      )
      return

    if not service_metadata.state.enableRules:
      track = self.ReleaseTrack()

      track_prefix = ''
      if track == base.ReleaseTrack.ALPHA:
        track_prefix = 'alpha '
      elif track == base.ReleaseTrack.BETA:
        track_prefix = 'beta '
      # GA commands do not have a 'ga' prefix, so it remains empty

      enable_command = f'gcloud {track_prefix}services enable {args.service}'
      log.warning(
          'To enable the MCP endpoint, the service must'
          ' be enabled first. Please run the following command to enable the'
          f' service: {enable_command}.'
      )
      return

    op = serviceusage.AddMcpEnableRule(
        args.service,
        project,
        folder=folder,
        organization=organization,
    )

    if args.async_:
      cmd = _OP_WAIT_CMD.format(op.name)
      log.status.Print(
          'Asynchronous operation is in progress... '
          'Use the following command to wait for its '
          f'completion:\n {cmd}'
      )
      return

    op = services_util.WaitOperation(op.name, serviceusage.GetOperationV2Beta)

    services_util.PrintOperation(op)
