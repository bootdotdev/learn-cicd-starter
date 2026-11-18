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
"""The gcloud Firestore databases restore command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.firestore import databases
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.firestore import flags
from googlecloudsdk.command_lib.firestore import util as utils
from googlecloudsdk.core import properties


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class RestoreFirestoreAPI(base.Command):
  """Restores a Cloud Firestore database from a backup.

  ## EXAMPLES

  To restore a database from a backup.

      $ {command}
      --source-backup=projects/PROJECT_ID/locations/LOCATION_ID/backups/BACKUP_ID
      --destination-database=DATABASE_ID

  To restore a database from a backup with tags.

      $ {command}
      --source-backup=projects/PROJECT_ID/locations/LOCATION_ID/backups/BACKUP_ID
      --destination-database=DATABASE_ID
      --tags=key1=value1,key2=value2

  To restore to a CMEK-enabled database.

      $ {command}
      --source-backup=projects/PROJECT_ID/locations/LOCATION_ID/backups/BACKUP_ID
      --destination-database=DATABASE_ID
      --encryption-type=customer-managed-encryption
      --kms-key-name=projects/PROJECT_ID/locations/LOCATION_ID/keyRings/KEY_RING_ID/cryptoKeys/CRYPTO_KEY_ID
  """

  @classmethod
  def Args(cls, parser):
    parser.add_argument(
        '--source-backup',
        metavar='SOURCE_BACKUP',
        type=str,
        required=True,
        help=textwrap.dedent("""\
            The source backup to restore from.

            For example, to restore from backup `cf9f748a-7980-4703-b1a1-d1ffff591db0` in us-east1:

            $ {command} --source-backup=projects/PROJECT_ID/locations/us-east1/backups/cf9f748a-7980-4703-b1a1-d1ffff591db0
            """),
    )
    flags.AddDestinationDatabase(parser, 'restore', 'backup')
    flags.AddEncryptionConfigGroup(parser, 'backup')
    flags.AddTags(parser, 'database')

  def Run(self, args):
    project = properties.VALUES.core.project.Get(required=True)
    return databases.RestoreDatabase(
        project,
        args.source_backup,
        args.destination_database,
        self.EncryptionConfig(args),
        args.tags,
    )

  def EncryptionConfig(self, args):
    return utils.ExtractEncryptionConfig(args)
