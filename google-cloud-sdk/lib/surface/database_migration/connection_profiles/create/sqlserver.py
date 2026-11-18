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
"""Command to create connection profiles for a database migration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.database_migration import resource_args
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.database_migration import flags
from googlecloudsdk.command_lib.database_migration.connection_profiles import create_helper
from googlecloudsdk.command_lib.database_migration.connection_profiles import flags as cp_flags
from googlecloudsdk.command_lib.database_migration.connection_profiles import sqlserver_flags
from googlecloudsdk.core.console import console_io

DETAILED_HELP = {
    'DESCRIPTION': (
        'Create a Database Migration Service connection profile for SQL Server.'
    ),
    'EXAMPLES': """\
        To create a source connection profile my-source-profile for SQL Server:

            $ {command} my-source-profile --region=us-central1
            --gcs-bucket=bucket-name --gcs-prefix=prefix/path

        To create a destination connection profile my-dest-profile for SQL
        Server:

            $ {command} my-dest-profile --region=us-central1
            --cloudsql-instance=cloudsql-id
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class _SQLServer(base.Command):
  """Create a Database Migration Service connection profile for SQL Server."""

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    resource_args.AddSqlServerConnectionProfileResourceArg(parser, 'to create')

    cp_flags.AddNoAsyncFlag(parser)
    cp_flags.AddDisplayNameFlag(parser)
    cp_flags.AddRoleFlag(parser)
    cp_flags.AddSslServerOnlyOrRequiredConfigGroup(parser)
    cp_flags.AddSslFlags(parser)
    sqlserver_flags.AddCloudSqlInstanceFlags(parser)
    sqlserver_flags.AddCpDetailsFlag(parser)
    cp_flags.AddDatabaseFlag(parser)
    flags.AddLabelsCreateFlags(parser)

  def Run(self, args):
    """Create a Database Migration Service connection profile.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A dict object representing the operations resource describing the create
      operation if the create was successful.
    """
    self._ValidateArgs(args)
    connection_profile_ref = args.CONCEPTS.connection_profile.Parse()
    parent_ref = connection_profile_ref.Parent().RelativeName()

    if args.prompt_for_password:
      args.password = console_io.PromptPassword('Please Enter Password: ')

    helper = create_helper.CreateHelper()
    return helper.create(
        self.ReleaseTrack(),
        parent_ref,
        connection_profile_ref,
        args,
        'SQLSERVER',
    )

  def _ValidateArgs(self, args):
    """Validates the arguments for the command."""
    self._ValidateHeterogeneousOrDagArgs(args)
    self._ValidateHomeogeneousDestinationArgs(args)

  def _ValidateHeterogeneousOrDagArgs(self, args):
    if args.IsKnownAndSpecified('dbm_port'):
      self._ValidateDagArgs(args)
    else:
      self._ValidateHeterogeneousArgs(args)

  def _ValidateHeterogeneousArgs(self, args):
    """Validates the arguments for heterogeneous source connection profiles."""
    if args.IsKnownAndSpecified('host'):
      if args.username is None:
        raise exceptions.BadArgumentException(
            '--username',
            'Username must be specified with --host.',
        )
      if args.password is None:
        raise exceptions.BadArgumentException(
            '--password',
            'Password must be specified with --host.',
        )
      if args.IsKnownAndSpecified('cloudsql_instance'):
        raise exceptions.BadArgumentException(
            '--cloudsql-instance',
            'Cloud SQL instance can not be used with --host.',
        )
      if args.IsKnownAndSpecified('cloudsql_project_id'):
        raise exceptions.BadArgumentException(
            '--cloudsql-project-id',
            'Cloud SQL project ID can not be used with --host.',
        )

  def _ValidateDagArgs(self, args):
    """Validates the arguments for DAG HMM source/destination connection profiles."""
    if not args.IsKnownAndSpecified('role'):
      raise exceptions.BadArgumentException(
          '--role',
          'Role must be specified with --dbm-port.',
      )
    if args.username is None:
      raise exceptions.BadArgumentException(
          '--username',
          'Username must be specified with --dbm-port.',
      )
    if (
        not args.IsKnownAndSpecified('cloudsql_instance')
        and args.IsKnownAndSpecified('role')
        and args.role == 'DESTINATION'
    ):
      raise exceptions.BadArgumentException(
          '--cloudsql-instance',
          'Cloud SQL instance must be specified with --dbm-port and'
          ' --role=DESTINATION.',
      )
    if args.IsKnownAndSpecified('cloudsql_project_id'):
      raise exceptions.BadArgumentException(
          '--cloudsql-project-id',
          'Cloud SQL project ID can not be used with --dbm-port.',
      )
    if args.IsKnownAndSpecified('database'):
      raise exceptions.BadArgumentException(
          '--database',
          'Database can not be used with --dbm-port.',
      )

  def _ValidateHomeogeneousDestinationArgs(self, args):
    """Validates the arguments for homeogeneous destination connection profiles."""
    if (
        not args.IsKnownAndSpecified('host')
        and args.IsKnownAndSpecified('role')
        and args.role == 'DESTINATION'
    ):
      if args.cloudsql_instance is None:
        raise exceptions.BadArgumentException(
            '--cloudsql-instance',
            'Cloud SQL instance must be specified with --role=DESTINATION.',
        )
      if args.IsKnownAndSpecified('gcs_bucket'):
        raise exceptions.BadArgumentException(
            '--gcs-bucket',
            'GCS bucket can not be used with --role=DESTINATION.',
        )
