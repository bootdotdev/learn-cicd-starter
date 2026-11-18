# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
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

"""services policies remove-enable-rule command."""

from googlecloudsdk.api_lib.services import services_util
from googlecloudsdk.api_lib.services import serviceusage
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.services import arg_parsers
from googlecloudsdk.command_lib.services import common_flags
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io

_PROJECT_RESOURCE = 'projects/{}'
_FOLDER_RESOURCE = 'folders/{}'
_ORGANIZATION_RESOURCE = 'organizations/{}'
_CONSUMER_POLICY_DEFAULT = '/consumerPolicies/{}'

_OP_BASE_CMD = 'gcloud beta services operations '
_OP_WAIT_CMD = _OP_BASE_CMD + 'wait {0}'


# TODO(b/321801975) make command public after preview.
@base.UniverseCompatible
@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class RemovedEnableRules(base.SilentCommand):
  """Remove service(s) from a consumer policy for a project, folder or organization.

  Remove service(s) from a consumer policy for a project, folder or
  organization.

  ## EXAMPLES
  To remove service called `my-consumed-service` from the default consumer
  policy on the current project, run:

    $ {command} my-consumed-service
        OR
    $ {command} my-consumed-service --policy-name=default

   To remove service called `my-consumed-service` from from the default consumer
   policy on project `my-project`, run:

    $ {command} my-consumed-service --project=my-project
        OR
    $ {command} my-consumed-service --policy-name=default

  To run the same command asynchronously (non-blocking), run:

    $ {command} my-consumed-service --async
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    common_flags.consumer_service_flag(
        suffix='to remove enable rule for'
    ).AddToParser(parser)
    parser.add_argument(
        '--policy-name',
        help=(
            'Name of the consumer policy. Currently only "default" is'
            ' supported.'
        ),
        default='default',
    )
    common_flags.add_resource_args(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    parser.add_argument(
        '--force',
        action='store_true',
        help=(
            'If specified, the remove-enable-rules call will proceed even if'
            ' there are enabled services which depend on the service to be'
            ' removed from enable rule or the service to be removed was used in'
            ' the last 30 days, or the service to be removed was enabled in the'
            ' last 3 days. Forcing the call means that the services which'
            ' depend on the service to be removed from the enable rule will'
            ' also be removed.'
        ),
    )
    common_flags.validate_only_args(parser, suffix='remove enable rule')

  def Run(self, args):
    """Run services policies remove-enable-rules.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      The services in the consumer policy.
    """

    project = (
        args.project
        if args.IsSpecified('project')
        else properties.VALUES.core.project.Get(required=True)
    )
    folder = args.folder if args.IsSpecified('folder') else None
    organization = (
        args.organization if args.IsSpecified('organization') else None
    )

    service_names = []

    for service_name in args.service:
      service_name = arg_parsers.GetServiceNameFromArg(service_name)

      protected_msg = serviceusage.GetProtectedServiceWarning(service_name)
      if protected_msg:
        if args.IsSpecified('quiet'):
          raise console_io.RequiredPromptError()
        do_disable = console_io.PromptContinue(
            protected_msg, default=False, throw_if_unattended=True
        )
        if not do_disable:
          continue
      service_names.append(service_name)

    op = serviceusage.RemoveEnableRule(
        project,
        service_names,
        args.policy_name,
        args.force,
        folder,
        organization,
        args.validate_only,
        skip_dependency_check=False,
        disable_dependency_services=args.force,
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
    if args.validate_only:
      services_util.PrintOperation(op)
    else:
      services_util.PrintOperationWithResponse(op)
