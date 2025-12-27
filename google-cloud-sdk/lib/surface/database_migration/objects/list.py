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
"""Implementation of migration job objects list command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.database_migration import objects
from googlecloudsdk.api_lib.database_migration import resource_args
from googlecloudsdk.calliope import base


class _MigrationJobObjectInfo:
  """Container for migration job object data using in list display."""

  def __init__(self, message):
    self.name = message.name
    self.source_object = message.sourceObject
    self.error = message.error if message.error is not None else None
    self.state = message.state
    self.phase = message.phase
    self.create_time = message.createTime
    self.update_time = message.updateTime


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class List(base.ListCommand):
  """List a DMS migration job objects.

  List migration job objects.

  ## API REFERENCE
    This command uses the database-migration/v1 API. The full documentation
    for this API can be found at: https://cloud.google.com/database-migration/

  ## EXAMPLES
    To list all objects in a migration job and location 'us-central1',
    run:

        $ {command} --migration-job=mj --region=us-central1
  """

  @classmethod
  def Args(cls, parser):
    """Register flags for this command."""
    resource_args.AddOnlyMigrationJobResourceArgs(
        parser, 'to list migration job objects', positional=False
    )
    parser.display_info.AddFormat("""
            table(
              source_object,
              state:label=STATE,
              phase:label=PHASE,
              error:label=ERROR
            )
          """)

  def Run(self, args):
    """Runs the command.

    Args:
      args: All the arguments that were provided to this command invocation.

    Returns:
      An iterator over objects containing migration job objects data.
    """
    objects_client = objects.ObjectsClient(self.ReleaseTrack())
    migration_job_ref = args.CONCEPTS.migration_job.Parse()
    obj = objects_client.List(migration_job_ref, args)

    return [_MigrationJobObjectInfo(o) for o in obj]
