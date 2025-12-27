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
"""The gcloud Firestore databases connection-string command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.firestore import databases
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.firestore import connection_util
from googlecloudsdk.command_lib.firestore import flags
from googlecloudsdk.core import properties


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class ConnectionString(base.Command):
  """Prints the mongo connection string for the given Firestore database.

  ## EXAMPLES

  To get the connection string for a Firestore database with a databaseId
  `testdb` without auth configuration.

      $ {command} --database=testdb --auth=none

  To get the connection string for a Firestore database with a databaseId
  `testdb` with Google Compute Engine VM auth.

      $ {command} --database=testdb --auth=gce-vm
  """

  _BASE_OUTPUT = 'mongodb://{}{}.{}.firestore.goog:443/{}?loadBalanced=true&tls=true&retryWrites=false'

  _GCE_VM_AUTH = '&authMechanism=MONGODB-OIDC&authMechanismProperties=ENVIRONMENT:gcp,TOKEN_RESOURCE:FIRESTORE'

  @staticmethod
  def Args(parser):
    flags.AddDatabaseIdFlag(parser, required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--validate',
        metavar='VALIDATE',
        required=False,
        hidden=False,
        type=str,
        help="""
        Validate the specified connection string for the current database. This
        command checks that the connection string is well formed, contains the
        required parameters, and specifies correct configuration values for the
        current database.
        """,
    )
    group.add_argument(
        '--auth',
        metavar='AUTH',
        required=False,
        hidden=False,
        type=str,
        choices=['none', 'gce-vm', 'access-token', 'scram-sha-256'],
        default='none',
        help="""
        The auth configuration for the connection string.

        If connecting from a Google Compute Engine VM, use `gce-vm`. For short
        term access using the gcloud CLI's access token, use `access-token`.
        For password auth use scram-sha-256. Otherwise, use `none` and configure
        auth manually.
        """,
    )

  def Run(self, args):
    project = properties.VALUES.core.project.Get(required=True)
    db = databases.GetDatabase(project, args.database)
    database_id = '_' if args.database == '(default)' else args.database
    if args.validate:
      connection_util.PrettyPrintValidationResults(
          connection_util.ValidateConnectionString(
              args.validate, db.uid, db.locationId, args.database
          )
      )
      return None
    elif args.auth == 'gce-vm':
      return (
          self._BASE_OUTPUT.format('', db.uid, db.locationId, database_id)
          + self._GCE_VM_AUTH
      )
    elif args.auth == 'access-token':
      return (
          self._BASE_OUTPUT.format(
              'access_token:$(gcloud auth print-access-token)@',
              db.uid,
              db.locationId,
              database_id,
          )
          + '&authMechanism=PLAIN&authSource=$external'
      )
    elif args.auth == 'scram-sha-256':
      return (
          self._BASE_OUTPUT.format(
              'username:password@',
              db.uid,
              db.locationId,
              database_id,
          )
          + '&authMechanism=SCRAM-SHA-256'
      )
    return self._BASE_OUTPUT.format('', db.uid, db.locationId, database_id)
