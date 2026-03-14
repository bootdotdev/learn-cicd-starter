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
"""Show the metadata for a Backup and DR backup vault."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from googlecloudsdk.api_lib.backupdr.backup_vaults import BackupVaultsClient
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.command_lib.backupdr import util as command_util


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Describe(base.DescribeCommand):
  """Show the metadata for a Backup and DR backup vault."""

  detailed_help = {
      'BRIEF': 'Show the metadata for a Backup and DR backup vault.',
      'DESCRIPTION': '{description}',
      'API REFERENCE': (
          'This command uses the backupdr/v1 API. The full documentation for'
          ' this API can be found at:'
          ' https://cloud.google.com/backup-disaster-recovery'
      ),
      'EXAMPLES': """\
        To view details associated with backup vault 'BACKUP_VAULT', run:

        $ {command} BACKUP_VAULT
        """,
  }

  DEFAULT_DESCRIBE_FORMAT = """
      json(
        name.basename(),
        description,
        createTime,
        updateTime,
        accessRestriction,
        deletable,
        state,
        totalStoredBytes,
        etag,
        serviceAccount,
        uid,
        backupCount,
        labels,
        backupMinimumEnforcedRetentionDuration,
        effectiveTime,
        backupRetentionInheritance
        )
        """

  @staticmethod
  def Args(parser):
    """Specifies additional command flags.

    Args:
      parser: argparse.Parser: Parser object for command line inputs.
    """

    flags.AddBackupVaultResourceArg(
        parser,
        'Name of the backup vault to retreive metadata of.',
    )
    flags.AddOutputFormat(parser, Describe.DEFAULT_DESCRIBE_FORMAT)

  def Run(self, args):
    client = BackupVaultsClient()
    backup_vault = args.CONCEPTS.backup_vault.Parse()
    bv_details = client.Describe(backup_vault)
    bv_details.backupMinimumEnforcedRetentionDuration = (
        command_util.TransformEnforcedRetention(bv_details)
    )
    return bv_details
