# -*- coding: utf-8 -*- #
# Copyright 2013 Google LLC. All Rights Reserved.
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
"""Deletes a Cloud SQL instance."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions

from googlecloudsdk.api_lib.sql import api_util
from googlecloudsdk.api_lib.sql import operations
from googlecloudsdk.api_lib.sql import validate
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.sql import flags
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io
import six


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.ALPHA)
class Delete(base.Command):
  """Deletes a Cloud SQL instance."""

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go
          on the command line after this command. Positional arguments are
          allowed.
    """
    base.ASYNC_FLAG.AddToParser(parser)
    parser.add_argument(
        'instance',
        completer=flags.InstanceCompleter,
        help='Cloud SQL instance ID.')
    flags.AddEnableFinalBackup(parser)
    flags.AddFinalbackupDescription(parser)
    expiration = parser.add_mutually_exclusive_group(required=False)
    flags.AddFinalBackupExpiryTimeArgument(expiration)
    flags.AddFinalbackupRetentionDays(expiration)

  def Run(self, args):
    """Deletes a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the delete
      operation if the delete was successful.
    """
    client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
    sql_client = client.sql_client
    sql_messages = client.sql_messages
    operation_ref = None

    validate.ValidateInstanceName(args.instance)
    instance_ref = client.resource_parser.Parse(
        args.instance,
        params={'project': properties.VALUES.core.project.GetOrFail},
        collection='sql.instances',
    )

    try:
      instance_resource = sql_client.instances.Get(
          sql_messages.SqlInstancesGetRequest(
              project=instance_ref.project, instance=instance_ref.instance
          )
      )
    except exceptions.HttpError as error:
      instance_resource = None
      # We do not want to raise an error here to be consistent with the
      # previous behavior. The Get and Delete have different IAM auth
      # permissions. GET requires READ, and DELETE requires WRITE.
      log.debug(
          'Ignoring the error to get instance resource : %s',
          six.text_type(error),
      )

    if (
        instance_resource is not None
        and instance_resource.settings.retainBackupsOnDelete
    ):
      prompt = (
          'All of the instance data will be lost except the existing backups'
          ' when the instance is deleted.'
      )
    else:
      # TODO(b/361801536): Update the message to a link that points to public
      # doc about how to retain the automated and ondemand backups.
      # As the feature is not yet public, we do not have a link right now.
      prompt = (
          'All of the instance data will be lost when the instance is deleted.'
      )

    if not console_io.PromptContinue(prompt):
      return None

    expiry_time = None
    if (
        args.final_backup_retention_days is not None
        and args.final_backup_retention_days > 0
    ):
      retention_days = args.final_backup_retention_days
    else:
      retention_days = None

    if args.final_backup_expiry_time is not None:
      expiry_time = args.final_backup_expiry_time.strftime(
          '%Y-%m-%dT%H:%M:%S.%fZ'
      )

    try:
      result = sql_client.instances.Delete(
          sql_messages.SqlInstancesDeleteRequest(
              instance=instance_ref.instance,
              project=instance_ref.project,
              enableFinalBackup=args.enable_final_backup,
              finalBackupTtlDays=retention_days,
              finalBackupDescription=args.final_backup_description,
              finalBackupExpiryTime=expiry_time,
          )
      )

      operation_ref = client.resource_parser.Create(
          'sql.operations', operation=result.name, project=instance_ref.project)

      if args.async_:
        return sql_client.operations.Get(
            sql_messages.SqlOperationsGetRequest(
                project=operation_ref.project,
                operation=operation_ref.operation))

      operations.OperationsV1Beta4.WaitForOperation(
          sql_client, operation_ref, 'Deleting Cloud SQL instance')

      log.DeletedResource(instance_ref)

    except exceptions.HttpError:
      log.debug('operation : %s', six.text_type(operation_ref))
      raise
