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

"""Performs pre-checks for a major version upgrade of a Cloud SQL instance."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import time

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.sql import api_util
from googlecloudsdk.api_lib.sql import validate
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.sql import flags
from googlecloudsdk.core import properties
import six.moves.http_client


DESCRIPTION = """
    *{command}* performs pre-checks for a major version upgrade of a Cloud SQL instance.
"""

EXAMPLES = """
    To perform pre-checks before upgrading to a target version:

      $ {command} test-instance --target-database-version=POSTGRES_15
"""

DETAILED_HELP = {
    'DESCRIPTION': DESCRIPTION,
    'EXAMPLES': EXAMPLES,
}


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class PreCheckMajorVersionUpgrade(base.Command):
  """Performs pre-checks for a major version upgrade of a Cloud SQL instance."""

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    base.ASYNC_FLAG.AddToParser(parser)
    parser.add_argument(
        'instance',
        completer=flags.InstanceCompleter,
        help='Cloud SQL instance ID.',
    )
    parser.add_argument(
        '--target-database-version',
        required=True,
        help='Target database version for the upgrade.',
    )

  def Run(self, args):
    client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
    sql_client = client.sql_client
    sql_messages = client.sql_messages

    validate.ValidateInstanceName(args.instance)
    instance_ref = client.resource_parser.Parse(
        args.instance,
        params={'project': properties.VALUES.core.project.GetOrFail},
        collection='sql.instances',
    )

    try:
      try:
        target_version_enum = sql_messages.PreCheckMajorVersionUpgradeContext.TargetDatabaseVersionValueValuesEnum(
            args.target_database_version.upper()
        )
      except TypeError:
        raise exceptions.InvalidArgumentException(
            'target-database-version',
            'Missing or Invalid parameter: Target database version.',
        )

      # Perform the pre-check
      request = sql_messages.SqlInstancesPreCheckMajorVersionUpgradeRequest(
          instance=args.instance,
          project=instance_ref.project,
          instancesPreCheckMajorVersionUpgradeRequest=
          sql_messages.InstancesPreCheckMajorVersionUpgradeRequest(
              preCheckMajorVersionUpgradeContext=sql_messages.PreCheckMajorVersionUpgradeContext(
                  targetDatabaseVersion=target_version_enum
              )
          )
      )

      result_operation = (
          sql_client.instances.PreCheckMajorVersionUpgrade(request)
      )

      operation_ref = client.resource_parser.Create(
          'sql.operations',
          operation=result_operation.name,
          project=instance_ref.project
      )

      if args.async_:
        return sql_client.operations.Get(
            sql_messages.SqlOperationsGetRequest(
                project=operation_ref.project, operation=operation_ref.operation
            )
        )

      # Custom polling logic instead of WaitForOperation
      while True:
        op = sql_client.operations.Get(
            sql_messages.SqlOperationsGetRequest(
                project=operation_ref.project,
                operation=operation_ref.operation
            )
        )
        if op.status == sql_messages.Operation.StatusValueValuesEnum.DONE:
          break
        time.sleep(1)

      context = getattr(op, 'preCheckMajorVersionUpgradeContext', None)
      precheck_responses = (
          getattr(context, 'preCheckResponse', []) if context else []
      )

      formatted_responses = []
      for resp in precheck_responses:
        raw_message = resp.message

          # Remove unwanted suffix if present
        if raw_message.endswith('"]'):
          raw_message = raw_message[:-2]

        clean_message = raw_message.strip().strip('"')
        if 'pre-upgrade check failed' not in clean_message:
          formatted_responses.append({
              'message': clean_message,
              'message_type': resp.messageType.name,
              'actions_required': resp.actionsRequired,
          })
      print('Performing pre-check on Cloud SQL instance....done')
      if precheck_responses:
        print(
            'Please check the'
            ' output in the PreCheckResults field for more details.'
        )
      else:
        print(
            'No issues or warnings detected during pre-check. We recommend that'
            ' you perform MVU on a cloned instance before applying them to a'
            ' production instance.'
        )
      return {
          'Name': instance_ref.instance,
          'Project': instance_ref.project,
          'TargetDatabaseVersion': (
              str(context.targetDatabaseVersion)
              if context
              else args.target_database_version.upper()
          ),
          'PreCheckResults': formatted_responses,
          'Status': 'COMPLETED',
      }

    except apitools_exceptions.HttpError as error:
      if error.status_code == six.moves.http_client.FORBIDDEN:
        raise exceptions.HttpException(
            "There's no instance found at {} or you're not authorized to"
            ' access it.'.format(instance_ref.RelativeName())
        )
      raise exceptions.HttpException(error)
