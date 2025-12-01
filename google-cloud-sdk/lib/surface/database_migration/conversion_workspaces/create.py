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
"""Command to create conversion workspaces for a database migration."""

import argparse
from typing import Optional, Type, TypeVar

from googlecloudsdk.api_lib.database_migration import resource_args
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.database_migration.conversion_workspaces import command_mixin
from googlecloudsdk.command_lib.database_migration.conversion_workspaces import flags as cw_flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.generated_clients.apis.datamigration.v1 import datamigration_v1_messages as messages

GlobalSettingsValue = TypeVar('GlobalSettingsValue')


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Create(command_mixin.ConversionWorkspacesCommandMixin, base.Command):
  """Create a Database Migration Service conversion workspace."""

  detailed_help = {
      'DESCRIPTION': """
        Create a Database Migration Service conversion workspace.
      """,
      'EXAMPLES': """\
        To create a conversion workspace:

            $ {command} my-conversion-workspace --region=us-central1
            --display-name=cw1
            --source-database-engine=ORACLE
            --source-database-version=11
            --destination-database-engine=POSTGRESQL
            --destination-database-version=15
      """,
  }

  @staticmethod
  def Args(parser: argparse.ArgumentParser) -> None:
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    resource_args.AddConversionWorkspaceResourceArg(parser, 'to create')
    cw_flags.AddNoAsyncFlag(parser)
    cw_flags.AddDisplayNameFlag(parser)
    cw_flags.AddDatabaseEngineFlags(parser)
    cw_flags.AddDatabaseProviderFlags(parser)
    cw_flags.AddDatabaseVersionFlag(parser)
    cw_flags.AddGlobalSettingsFlag(parser)

  def Run(self, args: argparse.Namespace) -> Optional[messages.Operation]:
    """Create a Database Migration Service conversion workspace.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A dict object representing the operations resource describing the create
      operation if the create was successful.
    """
    self._ValidateEngineProviderFlags(args)

    conversion_workspace_ref = args.CONCEPTS.conversion_workspace.Parse()

    result_operation = self.client.crud.Create(
        parent_ref=conversion_workspace_ref.Parent().RelativeName(),
        conversion_workspace_id=conversion_workspace_ref.conversionWorkspacesId,
        display_name=args.display_name,
        source_database_provider=args.source_database_provider,
        source_database_engine=args.source_database_engine,
        source_database_version=args.source_database_version,
        destination_database_provider=args.destination_database_provider,
        destination_database_engine=args.destination_database_engine,
        destination_database_version=args.destination_database_version,
        global_settings=self._BuildGlobalSettings(
            args=args,
            global_settings_value_cls=self.client.crud.messages.ConversionWorkspace.GlobalSettingsValue,
        ),
    )

    return self.HandleOperationResult(
        conversion_workspace_ref=conversion_workspace_ref,
        result_operation=result_operation,
        operation_name='Created',
        sync=args.IsKnownAndSpecified('no_async'),
    )

  def _ValidateEngineProviderFlags(self, args: argparse.Namespace) -> None:
    """Validates the engine and provider flags."""
    if (
        args.source_database_provider
        not in args.source_database_engine.supported_providers
    ):
      raise exceptions.InvalidArgumentException(
          '--source_database_engine, --source_database_provider',
          f'Source database engine {args.source_database_engine} is not'
          ' supported by the source database provider'
          f' {args.source_database_provider}.\nSupported providers are:'
          f' {", ".join(map(str, args.source_database_engine.supported_providers))}.',
      )

    if (
        args.destination_database_provider
        not in args.destination_database_engine.supported_providers
    ):
      raise exceptions.InvalidArgumentException(
          '--destination_database_engine, --destination_database_provider',
          f'Destination database engine {args.destination_database_engine} is'
          ' not supported by the destination database provider'
          f' {args.destination_database_provider}.\nSupported providers are:'
          f' {", ".join(map(str, args.destination_database_engine.supported_providers))}.',
      )

  def _BuildGlobalSettings(
      self,
      args: argparse.Namespace,
      global_settings_value_cls: Type[GlobalSettingsValue],
  ) -> GlobalSettingsValue:
    """Builds the global settings for the conversion workspace.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.
      global_settings_value_cls: The class to use for the global settings value.

    Returns:
      A global settings value object.
    """
    if args.global_settings is None:
      args.global_settings = {}
    args.global_settings.update(filter='*', v2='true')
    return labels_util.ParseCreateArgs(
        args=args,
        labels_cls=global_settings_value_cls,
        labels_dest='global_settings',
    )
