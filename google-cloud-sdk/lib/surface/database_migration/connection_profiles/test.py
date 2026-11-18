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
"""Command to test connection profiles for a database migration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from typing import Any

from googlecloudsdk.api_lib.database_migration import api_util
from googlecloudsdk.api_lib.database_migration import connection_profiles
from googlecloudsdk.api_lib.database_migration import resource_args
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.database_migration.connection_profiles import flags as cp_flags
from googlecloudsdk.core import log


DETAILED_HELP = {
    'DESCRIPTION': """
        Validates a Database Migration Service connection profile.
        """,
    'EXAMPLES': """\
        To test a connection profile:

            $ {command} my-profile --region=us-central1
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Test(base.Command):
  """Test a Database Migration Service connection profile."""

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser) -> None:
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    resource_args.AddConnectionProfileResourceArg(parser, 'to test')
    cp_flags.AddNoAsyncFlag(parser)

  def Run(self, args: Any) -> Any:
    """Test a Database Migration Service connection profile.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A dict object representing the operations resource describing the test
      operation.
    """
    connection_profile_ref = args.CONCEPTS.connection_profile.Parse()

    cp_client = connection_profiles.ConnectionProfilesClient(
        self.ReleaseTrack()
    )
    result_operation = cp_client.Test(connection_profile_ref.RelativeName())

    client = api_util.GetClientInstance(self.ReleaseTrack())
    messages = api_util.GetMessagesModule(self.ReleaseTrack())
    resource_parser = api_util.GetResourceParser(self.ReleaseTrack())

    if args.IsKnownAndSpecified('no_async'):
      log.status.Print(
          'Waiting for connection profile [{}] to be test with [{}]'.format(
              connection_profile_ref.connectionProfilesId, result_operation.name
          )
      )

      api_util.HandleLRO(
          client, result_operation, client.projects_locations_connectionProfiles
      )

      log.status.Print(
          'Tested connection profile {} [{}]'.format(
              connection_profile_ref.connectionProfilesId, result_operation.name
          )
      )
      return

    operation_ref = resource_parser.Create(
        'datamigration.projects.locations.operations',
        operationsId=result_operation.name,
        projectsId=connection_profile_ref.projectsId,
        locationsId=connection_profile_ref.locationsId,
    )

    return client.projects_locations_operations.Get(
        messages.DatamigrationProjectsLocationsOperationsGetRequest(
            name=operation_ref.operationsId
        )
    )
