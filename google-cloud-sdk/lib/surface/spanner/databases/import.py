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
"""Import data from various source files to Cloud Spanner."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.spanner import flags
from googlecloudsdk.command_lib.spanner import migration_backend
from googlecloudsdk.command_lib.util.apis import arg_utils
from googlecloudsdk.core.credentials import store


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Import(base.BinaryBackedCommand):
  """Import data from various source files to Cloud Spanner."""

  detailed_help = {
      'EXAMPLES':
          textwrap.dedent(text="""\
        To import data from a source file to Cloud Spanner:

          $ {command} --instance=instanceA --database=databaseA
          --table-name=tableA --source-uri=gs://bucket/data.csv --source-format=csv
          --schema-uri=gs://bucket/schema.json

          $ {command} --instance=instanceA --database=databaseA
          --source-uri=gs://bucket/dump.sql --source-format=mysqldump
      """),
  }

  @staticmethod
  def Args(parser):
    """Register the flags for this command."""
    flags.Instance(False).AddToParser(parser)
    flags.Database(False, True).AddToParser(parser)
    flags.TableName(False).AddToParser(parser)
    flags.SourceUri(True).AddToParser(parser)
    flags.SourceFormat(True).AddToParser(parser)
    flags.SchemaUri(False).AddToParser(parser)
    flags.CsvLineDelimiter(False).AddToParser(parser)
    flags.CsvFieldDelimiter(False).AddToParser(parser)
    flags.DatabaseDialect('Dialect for the spanner database').AddToParser(
        parser
    )

  def Run(self, args):
    """Run the import command."""
    auth_token = store.GetFreshAccessTokenIfEnabled(min_expiry_duration='1h')
    command_executor = migration_backend.SpannerMigrationWrapper()
    env_vars = migration_backend.GetEnvArgsForCommand(
        extra_vars={
            'GCLOUD_HB_PLUGIN': 'true',
            'GCLOUD_AUTH_PLUGIN': 'true',
            'GCLOUD_AUTH_ACCESS_TOKEN': auth_token,
        }
    )
    project = arg_utils.GetFromNamespace(args, '--project', use_defaults=True)
    response = command_executor(
        command='import',
        instance=args.instance,
        database=args.database,
        table_name=args.table_name,
        source_uri=args.source_uri,
        source_format=args.source_format,
        schema_uri=args.schema_uri,
        csv_line_delimiter=args.csv_line_delimiter,
        csv_field_delimiter=args.csv_field_delimiter,
        project=project,
        database_dialect=args.database_dialect,
        env=env_vars,
    )
    self.exit_code = response.exit_code
    return self._DefaultOperationResponseHandler(response)
