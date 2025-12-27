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
"""Implementation of migration job object lookup command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.database_migration import objects
from googlecloudsdk.api_lib.database_migration import resource_args
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.database_migration.objects import flags as objects_flags

DESCRIPTION = (
    'Lookup a migration job object by its source object identifier (e.g.'
    ' database)'
)
EXAMPLES = """\
    To lookup an existing migration job object:

        $ {command} --migration-job=my-job --location=us-central1 --database=my-database
   """


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Lookup(base.Command):
  """Lookup a DMS migration job object."""

  detailed_help = {'DESCRIPTION': DESCRIPTION, 'EXAMPLES': EXAMPLES}

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    resource_args.AddOnlyMigrationJobResourceArgs(
        parser, 'to list migration job objects', positional=False
    )
    objects_flags.AddSourceObjectIdentifierFlag(parser)

  def Run(self, args):
    """Lookup a DMS migration job object.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A dict object representing the looked up migration job object if the
      lookup was successful.
    """
    objects_client = objects.ObjectsClient(self.ReleaseTrack())
    migration_job_ref = args.CONCEPTS.migration_job.Parse()

    return objects_client.Lookup(migration_job_ref, args)
