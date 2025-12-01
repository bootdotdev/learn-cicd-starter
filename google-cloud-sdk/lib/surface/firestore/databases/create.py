# -*- coding: utf-8 -*- #
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""Command to create a Cloud Firestore Database."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.firestore import api_utils
from googlecloudsdk.api_lib.firestore import databases
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.firestore import flags
from googlecloudsdk.core import properties


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
class CreateFirestoreAPI(base.Command):
  """Create a Google Cloud Firestore database via Firestore API.

  ## EXAMPLES

  To create a Firestore Enterprise database named `foo` in `nam5` for use with
  MongoDB Compatibility.

      $ {command} --database=foo --edition=enterprise --location=nam5

  To create a Firestore Native database in `nam5`.

      $ {command} --location=nam5

  To create a Firestore Native database in `us-central1` with tags.

      $ {command} --location=us-central1 --tags=key1=value1,key2=value2

  To create a Datastore Mode database in `us-east1`.

      $ {command} --location=us-east1 --type=datastore-mode

  To create a Datastore Mode database in `us-east1` with a databaseId `foo`.

      $ {command} --database=foo --location=us-east1 --type=datastore-mode

  To create a Firestore Native database in `nam5` with delete protection
  enabled.

      $ {command} --location=nam5 --delete-protection

  To create a Firestore Native database in `nam5` with Point In Time Recovery
  (PITR) enabled.

      $ {command} --location=nam5 --enable-pitr

  To create a Firestore Native database in `nam5` encrypted by a
  Customer-managed encryption key (CMEK).

      $ {command}
      --location=nam5
      --kms-key-name=projects/PROJECT_ID/locations/us/keyRings/KEY_RING_ID/cryptoKeys/CRYPTO_KEY_ID
  """

  def DatabaseType(self, database_type):
    if database_type == 'firestore-native':
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.TypeValueValuesEnum.FIRESTORE_NATIVE
      )
    elif database_type == 'datastore-mode':
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.TypeValueValuesEnum.DATASTORE_MODE
      )
    else:
      raise ValueError('invalid database type: {}'.format(database_type))

  def DatabaseEdition(self, database_edition):
    if database_edition == 'standard':
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.DatabaseEditionValueValuesEnum.STANDARD
      )
    elif database_edition == 'enterprise':
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.DatabaseEditionValueValuesEnum.ENTERPRISE
      )
    else:
      raise ValueError('invalid database edition: {}'.format(database_edition))

  def DatabaseDeleteProtectionState(self, enable_delete_protection):
    if enable_delete_protection:
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.DeleteProtectionStateValueValuesEnum.DELETE_PROTECTION_ENABLED
      )
    return (
        api_utils.GetMessages().GoogleFirestoreAdminV1Database.DeleteProtectionStateValueValuesEnum.DELETE_PROTECTION_DISABLED
    )

  def DatabasePitrState(self, enable_pitr):
    if enable_pitr is None:
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.PointInTimeRecoveryEnablementValueValuesEnum.POINT_IN_TIME_RECOVERY_ENABLEMENT_UNSPECIFIED
      )
    if enable_pitr:
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.PointInTimeRecoveryEnablementValueValuesEnum.POINT_IN_TIME_RECOVERY_ENABLED
      )
    return (
        api_utils.GetMessages().GoogleFirestoreAdminV1Database.PointInTimeRecoveryEnablementValueValuesEnum.POINT_IN_TIME_RECOVERY_DISABLED
    )

  def DatabaseCmekConfig(self, args):
    if args.kms_key_name is not None:
      return api_utils.GetMessages().GoogleFirestoreAdminV1CmekConfig(
          kmsKeyName=args.kms_key_name
      )
    return api_utils.GetMessages().GoogleFirestoreAdminV1CmekConfig()

  def Run(self, args):
    project = properties.VALUES.core.project.Get(required=True)
    return databases.CreateDatabase(
        project,
        args.location,
        args.database,
        self.DatabaseType(args.type),
        self.DatabaseEdition(args.edition),
        self.DatabaseDeleteProtectionState(args.delete_protection),
        self.DatabasePitrState(args.enable_pitr),
        self.DatabaseCmekConfig(args),
        mongodb_compatible_data_access_mode=None,
        firestore_data_access_mode=None,
        realtime_updates_mode=None,
        tags=args.tags,
    )

  @classmethod
  def Args(cls, parser):
    flags.AddLocationFlag(
        parser, required=True, suggestion_aliases=['--region']
    )
    parser.add_argument(
        '--edition',
        help='The edition of the database.',
        default='standard',
        choices=['standard', 'enterprise'],
    )
    parser.add_argument(
        '--type',
        help='The type of the database.',
        default='firestore-native',
        choices=['firestore-native', 'datastore-mode'],
    )
    parser.add_argument(
        '--database',
        help=textwrap.dedent("""\
            The ID to use for the database, which will become the final
            component of the database's resource name. If database ID is not
            provided, (default) will be used as database ID.

            This value should be 4-63 characters. Valid characters are /[a-z][0-9]-/
            with first character a letter and the last a letter or a number. Must
            not be UUID-like /[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}/.

            Using "(default)" database ID is also allowed.
            """),
        type=str,
        default='(default)',
    )
    parser.add_argument(
        '--delete-protection',
        help=textwrap.dedent("""\
            Whether to enable delete protection on the created database.

            If set to true, delete protection of the new database will be enabled
            and delete operations will fail unless delete protection is disabled.

            Default to false.
            """),
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '--enable-pitr',
        help=textwrap.dedent("""\
            Whether to enable Point In Time Recovery (PITR) on the created database.

            If set to true, PITR on the new database will be enabled. By default, this feature is not enabled.
            """),
        action='store_true',
        default=None,
    )
    flags.AddKmsKeyNameFlag(parser)
    flags.AddTags(parser, 'database')


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateFirestoreAPIAlpha(CreateFirestoreAPI):
  """Create a Google Cloud Firestore database via Firestore API.

  ## EXAMPLES

  To create a Firestore Enterprise database named `foo` in `nam5` for use with
  MongoDB Compatibility.

      $ {command} --database=foo --edition=enterprise --location=nam5

  To create a Firestore Native database in `nam5`.

      $ {command} --location=nam5

  To create a Firestore Native database in `us-central1` with tags.

      $ {command} --location=us-central1 --tags=key1=value1,key2=value2

  To create a Datastore Mode database in `us-east1`.

      $ {command} --location=us-east1 --type=datastore-mode

  To create a Datastore Mode database in `us-east1` with a databaseId `foo`.

      $ {command} --database=foo --location=us-east1 --type=datastore-mode

  To create a Firestore Native database in `nam5` with delete protection
  enabled.

      $ {command} --location=nam5 --delete-protection

  To create a Firestore Native database in `nam5` with Point In Time Recovery
  (PITR) enabled.

      $ {command} --location=nam5 --enable-pitr

  To create a Firestore Native database in `nam5` encrypted by a
  Customer-managed encryption key (CMEK).

      $ {command}
      --location=nam5
      --kms-key-name=projects/PROJECT_ID/locations/us/keyRings/KEY_RING_ID/cryptoKeys/CRYPTO_KEY_ID
  """

  def MongodbCompatibleDataAccessMode(self, enable):
    if enable is None:
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.MongodbCompatibleDataAccessModeValueValuesEnum.DATA_ACCESS_MODE_UNSPECIFIED
      )
    if enable:
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.MongodbCompatibleDataAccessModeValueValuesEnum.DATA_ACCESS_MODE_ENABLED
      )
    return (
        api_utils.GetMessages().GoogleFirestoreAdminV1Database.MongodbCompatibleDataAccessModeValueValuesEnum.DATA_ACCESS_MODE_DISABLED
    )

  def FirestoreDataAccessMode(self, enable):
    if enable is None:
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.FirestoreDataAccessModeValueValuesEnum.DATA_ACCESS_MODE_UNSPECIFIED
      )
    if enable:
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.FirestoreDataAccessModeValueValuesEnum.DATA_ACCESS_MODE_ENABLED
      )
    return (
        api_utils.GetMessages().GoogleFirestoreAdminV1Database.FirestoreDataAccessModeValueValuesEnum.DATA_ACCESS_MODE_DISABLED
    )

  def RealtimeUpdatesMode(self, enable):
    if enable is None:
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.RealtimeUpdatesModeValueValuesEnum.REALTIME_UPDATES_MODE_UNSPECIFIED
      )
    if enable:
      return (
          api_utils.GetMessages().GoogleFirestoreAdminV1Database.RealtimeUpdatesModeValueValuesEnum.REALTIME_UPDATES_MODE_ENABLED
      )
    return (
        api_utils.GetMessages().GoogleFirestoreAdminV1Database.RealtimeUpdatesModeValueValuesEnum.REALTIME_UPDATES_MODE_DISABLED
    )

  def Run(self, args):
    project = properties.VALUES.core.project.Get(required=True)
    return databases.CreateDatabase(
        project,
        args.location,
        args.database,
        self.DatabaseType(args.type),
        self.DatabaseEdition(args.edition),
        self.DatabaseDeleteProtectionState(args.delete_protection),
        self.DatabasePitrState(args.enable_pitr),
        self.DatabaseCmekConfig(args),
        self.MongodbCompatibleDataAccessMode(
            args.enable_mongodb_compatible_data_access
        ),
        self.FirestoreDataAccessMode(args.enable_firestore_data_access),
        self.RealtimeUpdatesMode(args.enable_realtime_updates),
        args.tags,
    )

  @classmethod
  def Args(cls, parser):
    CreateFirestoreAPI.Args(parser)
    parser.add_argument(
        '--enable-mongodb-compatible-data-access',
        help=textwrap.dedent("""\
            Whether to enable MongoDB Compatible API Data Access on the
            created database.

            If set to true, MongoDB Compatible API Data Access on the new
            database will be enabled. By default, this feature is enabled for
            Enterprise edition databases.
            To disable, use --no-enable-mongodb-compatible-data-access.
            """),
        action='store_true',
        default=None,
        hidden=True,
    )
    parser.add_argument(
        '--enable-firestore-data-access',
        help=textwrap.dedent("""\
            Whether to enable Firestore API Data Access on the created
            database.

            If set to true, Firestore API Data Access on the new database will
            be enabled. By default, this feature is disabled for Enterprise
            edition databases. To explicitly disable,
            use --no-enable-firestore-data-access.
            """),
        action='store_true',
        default=None,
        hidden=True,
    )
    parser.add_argument(
        '--enable-realtime-updates',
        help=textwrap.dedent("""\
            Whether to enable Realtime Updates feature on the created database.

            If set to true, Realtime Updates feature on the new database will
            be enabled. By default, this feature is disabled for Enterprise
            edition databases. To explicitly disable,
            use --no-enable-realtime-updates.
            """),
        action='store_true',
        default=None,
        hidden=True,
    )
