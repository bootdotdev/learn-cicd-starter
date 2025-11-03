# -*- coding: utf-8 -*- #
# Copyright 2018 Google LLC. All Rights Reserved.
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
"""The gcloud datastore indexes create command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.app import yaml_parsing
from googlecloudsdk.api_lib.datastore import constants
from googlecloudsdk.api_lib.datastore import index_api
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.calliope import parser_arguments
from googlecloudsdk.command_lib.app import output_helpers
from googlecloudsdk.command_lib.datastore import flags
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
class Create(base.Command):
  """Create Cloud Datastore indexes."""

  detailed_help = {
      'brief': (
          'Create new datastore indexes based on your local index '
          'configuration.'
      ),
      'DESCRIPTION': """
Create new datastore indexes based on your local index configuration.
Any indexes in your index file that do not exist will be created.
      """,
      'EXAMPLES': """\
          To create new indexes based on your local configuration, run:

            $ {command} ~/myapp/index.yaml

          Detailed information about index configuration can be found at the
          [index.yaml reference](https://cloud.google.com/datastore/docs/tools/indexconfig).
          """,
  }

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor) -> None:
    """Get arguments for this command."""
    flags.AddIndexFileFlag(parser)
    flags.AddDatabaseIdFlag(parser)

  def Run(self, args) -> None:
    """Create missing indexes as defined in the index.yaml file."""
    # Default to '(default)' if unset.
    database_id = (
        args.database if args.database else constants.DEFAULT_NAMESPACE
    )
    self.CreateIndexes(
        index_file=args.index_file, database=database_id, enable_vector=False
    )

  def CreateIndexes(
      self, index_file: str, database: str, enable_vector: bool
  ) -> None:
    """Cleates missing indexes via the Firestore Admin API.

    Lists the database's existing indexes, and then compares them against the
    indexes that are defined in the given index.yaml file. Any discrepancies
    against the index.yaml file are created.

    Args:
      index_file: The users definition of their desired indexes.
      database: The database within the project we are operating on.
      enable_vector: Whether or not vector indexes are supported.
    """
    project = properties.VALUES.core.project.Get(required=True)
    info = yaml_parsing.ConfigYamlInfo.FromFile(index_file)
    if not info or info.name != yaml_parsing.ConfigYamlInfo.INDEX:
      raise exceptions.InvalidArgumentException(
          'index_file', 'You must provide the path to a valid index.yaml file.'
      )
    output_helpers.DisplayProposedConfigDeployments(
        project=project, configs=[info]
    )
    console_io.PromptContinue(
        default=True, throw_if_unattended=False, cancel_on_no=True
    )

    index_api.CreateMissingIndexesViaFirestoreApi(
        project_id=project,
        database_id=database,
        index_definitions=info.parsed,
        enable_vector=enable_vector,
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateFirestoreAPI(Create):
  """Create Cloud Datastore indexes with Firestore API."""

  def Run(self, args) -> None:
    # Default to '(default)' if unset.
    database_id = (
        constants.DEFAULT_NAMESPACE if not args.database else args.database
    )
    return self.CreateIndexes(
        index_file=args.index_file, database=database_id, enable_vector=True
    )
