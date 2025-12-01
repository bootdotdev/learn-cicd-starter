# -*- coding: utf-8 -*- #
# Copyright 2013 Google LLC. All Rights Reserved.
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
"""Reset SSL materials according to the reset SSL mode."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.sql import api_util
from googlecloudsdk.api_lib.sql import operations
from googlecloudsdk.api_lib.sql import validate
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.sql import flags
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class ResetSslConfigBase(base.Command):
  """Reset SSL materials according to the reset SSL mode."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    AddBaseArgs(parser)

  def Run(self, args):
    """Reset SSL materials according to the reset SSL mode.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A dict object representing the operations resource describing the
      resetSslConfig operation if the reset was successful.
    """
    return RunBaseResetSslConfigCommand(args, self.ReleaseTrack())


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class ResetSslConfigBeta(base.Command):
  """Reset SSL materials according to the reset SSL mode."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    AddBaseArgs(parser)
    AddBetaArgs(parser)

  def Run(self, args):
    """Reset SSL materials according to the reset SSL mode.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A dict object representing the operations resource describing the
      resetSslConfig operation if the reset was successful.
    """
    return RunBaseResetSslConfigCommand(args, self.ReleaseTrack())


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ResetSslConfigAlpha(base.Command):
  """Reset SSL materials according to the reset SSL mode."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    AddBaseArgs(parser)
    AddBetaArgs(parser)
    AddAlphaArgs(parser)

  def Run(self, args):
    """Reset SSL materials according to the reset SSL mode.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A dict object representing the operations resource describing the
      resetSslConfig operation if the reset was successful.
    """
    return RunBaseResetSslConfigCommand(args, self.ReleaseTrack())


def RunBaseResetSslConfigCommand(args, release_track):
  """Reset SSL materials according to the reset SSL mode.

  Args:
    args: argparse.Namespace, The arguments that this command was invoked with.
    release_track: string, The release track GA/BETA/ALPHA.

  Returns:
    A dict object representing the operations resource describing the
    resetSslConfig operation if the reset was successful.
  """
  client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
  sql_client = client.sql_client
  sql_messages = client.sql_messages

  validate.ValidateInstanceName(args.instance)
  instance_ref = client.resource_parser.Parse(
      args.instance,
      params={'project': properties.VALUES.core.project.GetOrFail},
      collection='sql.instances',
  )

  req = sql_messages.SqlInstancesResetSslConfigRequest(
      project=instance_ref.project, instance=instance_ref.instance
  )
  prompt_msg = (
      'Resetting your SSL configuration will delete all client certificates and'
      ' generate a new server certificate.'
  )
  if args.IsSpecified('mode'):
    req.mode = sql_messages.SqlInstancesResetSslConfigRequest.ModeValueValuesEnum.lookup_by_name(
        args.mode.upper()
    )
    if args.mode == 'SYNC_FROM_PRIMARY':
      prompt_msg = (
          'Syncing related SSL configs from the primary may cause SSL update'
          ' operations if needed.'
      )
  if IsBetaOrNewer(release_track):
    pass  # future beta arguments go here

  console_io.PromptContinue(message=prompt_msg, default=True, cancel_on_no=True)

  result_operation = sql_client.instances.ResetSslConfig(req)

  operation_ref = client.resource_parser.Create(
      'sql.operations',
      operation=result_operation.name,
      project=instance_ref.project,
  )

  if args.async_:
    return sql_client.operations.Get(
        sql_messages.SqlOperationsGetRequest(
            project=operation_ref.project, operation=operation_ref.operation
        )
    )

  operations.OperationsV1Beta4.WaitForOperation(
      sql_client, operation_ref, 'Resetting SSL config'
  )

  log.status.write(
      'Reset SSL config for [{resource}].\n'.format(resource=instance_ref)
  )


def AddAlphaArgs(unused_parser):
  """Adds alpha args and flags to the parser."""
  pass


def AddBetaArgs(unused_parser):
  """Adds beta args and flags to the parser."""
  pass


def AddBaseArgs(parser):
  """Adds base args and flags to the parser."""
  base.ASYNC_FLAG.AddToParser(parser)
  parser.add_argument(
      'instance',
      completer=flags.InstanceCompleter,
      help='Cloud SQL instance ID.',
  )
  parser.add_argument(
      '--mode',
      choices={
          'ALL': 'Refresh all TLS configs. This is the default behaviour.',
          'SYNC_FROM_PRIMARY': (
              'Refreshes the replication-related TLS configuration settings'
              ' provided by the primary instance. Not applicable to'
              ' on-premises replication instances.'
          ),
      },
      required=False,
      default=None,
      help='Selectively refresh the SSL materials',
  )


def IsBetaOrNewer(release_track):
  """Returns true if the release track is beta or newer."""
  return (
      release_track == base.ReleaseTrack.BETA
      or release_track == base.ReleaseTrack.ALPHA
  )
