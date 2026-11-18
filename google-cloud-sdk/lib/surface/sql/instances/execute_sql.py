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
"""Executes a statement on a Cloud SQL instance."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.sql import api_util
from googlecloudsdk.api_lib.sql import validate
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.sql import flags
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import files

DESCRIPTION = """\
    Executes a statement on a Cloud SQL instance. It will use the
    credentials of the specified Google Cloud account to connect to the
    instance, so an IAM user with the same name must exist in the instance.
    It doesn't support DQL or DML statements yet.
    WARNING: The requests and responses might transit through intermediate
    locations between your client and the location of the target instance.
    """

EXAMPLES = """\
    To execute a statement on a Cloud SQL instance, run:

    $ {command} instance-foo --sql="ALTER TABLE employees RENAME TO personnel;" --database=db1
    """

DETAILED_HELP = {
    'DESCRIPTION': DESCRIPTION,
    'EXAMPLES': EXAMPLES,
}


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
@base.DefaultUniverseOnly
class ExecuteSql(base.Command):
  """Executes a statement on a Cloud SQL instance."""

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    parser.add_argument(
        'instance',
        completer=flags.InstanceCompleter,
        help='Cloud SQL instance ID.',
    )
    parser.add_argument(
        '--sql',
        required=True,
        help=(
            'SQL statement(s) to execute. It supports multiple statements as'
            " well. When it starts with the character '@', the rest should be a"
            ' filepath to read the SQL statement(s) from.'
        ),
    )
    parser.add_argument(
        '--row_limit',
        type=int,
        required=False,
        help='Maximum number of rows to return. The default is unlimited.',
    )
    parser.add_argument(
        '--partial_result_mode',
        choices={
            'PARTIAL_RESULT_MODE_UNSPECIFIED': (
                'Unspecified mode, effectively the same as'
                ' `FAIL_PARTIAL_RESULT`.'
            ),
            'FAIL_PARTIAL_RESULT': (
                "Throw an error if the complete result can't be returned."
                " Don't return the partial result."
            ),
            'ALLOW_PARTIAL_RESULT': (
                'Return the partial result and mark the field partial_result to'
                " true if the complete result can't be returned. Don't throw"
                ' an error.'
            ),
        },
        required=False,
        default=None,
        help=(
            'Controls how the API should respond when the SQL execution result'
            ' is incomplete due to size limit or other reasons. The default'
            ' mode is to throw an error instead of returning the partial'
            ' result.'
        ),
    )
    flags.AddDatabase(
        parser,
        'Database on which the statement is executed.',
    )

  def Run(self, args):
    """Executes a statement on a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A dict object representing the execution result.
    """
    client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
    sql_client = client.sql_client
    sql_messages = client.sql_messages

    validate.ValidateInstanceName(args.instance)
    instance_ref = client.resource_parser.Parse(
        args.instance,
        params={'project': properties.VALUES.core.project.GetOrFail},
        collection='sql.instances',
    )
    if args.sql.startswith('@'):
      sql = files.ReadFileContents(args.sql[1:])
    else:
      sql = args.sql
    if args.partial_result_mode:
      partial_result_mode = sql_messages.ExecuteSqlPayload.PartialResultModeValueValuesEnum.lookup_by_name(
          args.partial_result_mode
      )
    else:
      partial_result_mode = None
    req_body = sql_messages.ExecuteSqlPayload(
        sqlStatement=sql,
        database=args.database,
        rowLimit=args.row_limit,
        partialResultMode=partial_result_mode,
        autoIamAuthn=True,
    )
    return sql_client.instances.ExecuteSql(
        sql_messages.SqlInstancesExecuteSqlRequest(
            instance=instance_ref.instance,
            project=instance_ref.project,
            executeSqlPayload=req_body,
        ),
    )
