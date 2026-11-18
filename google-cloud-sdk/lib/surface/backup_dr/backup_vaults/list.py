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
"""List Backup and DR backup vaults."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from googlecloudsdk.api_lib.backupdr.backup_vaults import BackupVaultsClient
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.backupdr import flags


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class List(base.ListCommand):
  """List Backup and DR backup vaults."""

  detailed_help = {
      'BRIEF': 'List Backup and DR backup vaults.',
      'DESCRIPTION': '{description}',
      'API REFERENCE': (
          'This command uses the backupdr/v1 API. The full documentation for'
          ' this API can be found at:'
          ' https://cloud.google.com/backup-disaster-recovery'
      ),
      'EXAMPLES': """\
        To list backup vaults in all location, run:

        $ {command}

        To list backup vaults in a location ''my-location'', run:

        $ {command} --location=my-location
        """,
  }

  DEFAULT_LIST_FORMAT = """
      table(
        name.basename(),
        createTime:label=CREATED,
        state:label=STATUS,
        name.scope("locations").segment(0):label=LOCATION,
        totalStoredBytes:label=STORED_BYTES,
        backupMinimumEnforcedRetentionDuration():label=BACKUP_MINIMUM_ENFORCED_RETENTION_DURATION
        )
        """

  @staticmethod
  def Args(parser):
    """Specifies additional command flags.

    Args:
      parser: argparse.Parser: Parser object for command line inputs.
    """

    flags.AddOutputFormat(parser, List.DEFAULT_LIST_FORMAT)
    flags.AddLocationResourceArg(
        parser,
        'Location for which backup vaults should be listed.',
        default='-',
    )
    parser.display_info.AddCacheUpdater(None)

  def Run(self, args):
    parent_ref = args.CONCEPTS.location.Parse()
    client = BackupVaultsClient()
    return client.List(parent_ref)
