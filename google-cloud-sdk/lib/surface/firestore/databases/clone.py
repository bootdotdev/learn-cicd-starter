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
"""The gcloud Firestore databases clone command."""

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
    base.ReleaseTrack.ALPHA)
class Clone(base.Command):
  """Clone a Google Cloud Firestore database from another.

  ## EXAMPLES

  To clone a database from another:

      $ gcloud alpha firestore databases clone
        --source-database=projects/PROJECT_ID/databases/SOURCE_DATABASE
        --snapshot-time=2025-05-26T10:20:00.00Z
        --destination-database=DATABASE_ID

  To clone to a CMEK-enabled database:

      $ gcloud alpha firestore databases clone
        --source-database=projects/PROJECT_ID/databases/SOURCE_DATABASE
        --snapshot-time=2025-05-26T10:20:00.00Z
        --destination-database=DATABASE_ID
        --encryption-type=customer-managed-encryption
        --kms-key-name=projects/PROJECT_ID/locations/LOCATION_ID/keyRings/KEY_RING_ID/cryptoKeys/CRYPTO_KEY_ID
  """

  @classmethod
  def Args(cls, parser):
    parser.add_argument(
        '--source-database',
        metavar='SOURCE_DATABASE',
        type=str,
        required=True,
        help=textwrap.dedent("""\
            The source database to clone from.

            For example, to clone from database
            source-db:

            $ {command} --source-database=projects/PROJECT_ID/databases/source-db
        """),
    )
    parser.add_argument(
        '--snapshot-time',
        metavar='SNAPSHOT_TIME',
        type=str,
        required=True,
        help=textwrap.dedent("""\
            Snapshot time at which to clone. This must be a whole minute, in the past, and not earlier than the source database's earliest_version_time.
            Additionally, if older than one hour in the past, PITR must be enabled on the source database.

            For example, to restore from snapshot `2025-05-26T10:20:00.00Z` of source database `source-db`:

            $ {command} --source-database=projects/PROJECT_ID/databases/source-db --snapshot-time=2025-05-26T10:20:00.00Z
        """),
    )
    flags.AddDestinationDatabase(parser, 'clone', 'database')
    flags.AddEncryptionConfigGroup(parser, 'database')
    flags.AddTags(parser, 'database')

  def Run(self, args):
    project = properties.VALUES.core.project.Get(required=True)
    return databases.CloneDatabase(
        project,
        args.source_database,
        args.snapshot_time,
        args.destination_database,
        self.EncryptionConfig(args),
        args.tags,
    )

  def EncryptionConfig(self, args):
    return utils.ExtractEncryptionConfig(args)
