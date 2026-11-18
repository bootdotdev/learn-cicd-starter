# -*- coding: utf-8 -*- #
# Copyright 2016 Google LLC. All Rights Reserved.
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
"""Restores a backup of a Cloud SQL instance."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.sql import api_util
from googlecloudsdk.api_lib.sql import exceptions
from googlecloudsdk.api_lib.sql import operations
from googlecloudsdk.api_lib.sql import validate
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.sql import constants
from googlecloudsdk.command_lib.sql import flags
from googlecloudsdk.command_lib.sql import instances as command_util
from googlecloudsdk.command_lib.sql import validate as command_validate
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io


def _ValidateBackupRequest(is_project_backup, args, overrides):
  """Validates the backup request.

  Args:
    is_project_backup: bool, Whether the backup request is for a project level
      backup.
    args: argparse.Namespace, The arguments that this command was invoked with.
    overrides: list[str], The list of flags that were overridden.
  """
  validate.ValidateInstanceName(args.restore_instance)
  if command_validate.IsBackupDrBackupRequest(args.id) or is_project_backup:
    if args.backup_project:
      raise exceptions.ArgumentError(
          ' --backup-project is not supported when using backup name based'
          ' restore command.'
      )

    if args.backup_instance:
      raise exceptions.ArgumentError(
          ' --backup-instance is not supported when using backup name based'
          ' restore command.'
      )
  else:
    if overrides:
      raise exceptions.ArgumentError(
          'Overrides are only supported for backup name based restore to new'
          f' instance. Unsupported flags: {overrides}'
      )


def _GetRestoreBackupRequest(args, sql_messages, instance_ref):
  """Get the restore backup request.

  Args:
    args: argparse.Namespace, The arguments that this command was invoked with.
    sql_messages: sql_v1beta4_messages.SqlMessagesV1Beta4, The SQL API messages.
    instance_ref: base.ResourceParse, The parsed instance reference.

  Returns:
    A SqlInstancesRestoreBackupRequest.
  """
  if command_validate.IsBackupDrBackupRequest(args.id):
    return sql_messages.SqlInstancesRestoreBackupRequest(
        project=instance_ref.project,
        instance=instance_ref.instance,
        instancesRestoreBackupRequest=sql_messages.InstancesRestoreBackupRequest(
            backupdrBackup=args.id
        ),
    )
  else:
    return sql_messages.SqlInstancesRestoreBackupRequest(
        project=instance_ref.project,
        instance=instance_ref.instance,
        instancesRestoreBackupRequest=sql_messages.InstancesRestoreBackupRequest(
            backup=args.id
        ),
    )


def _GetRestoreInstanceClearOverrides(args):
  """Get the database instance clear overrides.

  Args:
    args: argparse.Namespace, The arguments that this command was invoked with.

  Returns:
    An array with the database instance fields that should be cleared.
  """
  cleared_fields = []

  if args.IsKnownAndSpecified('clear_network'):
    cleared_fields.append('settings.ip_configuration.private_network')

  if args.clear_active_directory_dns_servers:
    cleared_fields.append('settings.active_directory_config.dns_servers')

  if args.IsKnownAndSpecified('clear_disk_encryption'):
    cleared_fields.append('disk_encryption_config')

  if args.clear_active_directory:
    cleared_fields.append('settings.active_directory_config')

  return cleared_fields


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.GA, base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA
)
class RestoreBackup(base.RestoreCommand):
  """Restores a backup of a Cloud SQL instance.

  The command lets you restore to an existing instance using ID. To restore
  using a backupDR backup, use the backupDR ID. When backup Name is used to
  restore it lets you restore to an existing instance or a new instance. When
  restoring to new instance, optional flags can be used to customize the new
  instance.
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.AddBackupId(
        parser,
        help_text=(
            'The ID of the backup run to restore from or the backup NAME for'
            ' restore to existing/new instance. To find the NAME, run the'
            ' following command:'
            ' $ gcloud sql backups list --filter=instance:{instance}'
        ),
    )
    parser.add_argument(
        '--restore-instance',
        required=True,
        completer=flags.InstanceCompleter,
        help=(
            'The ID of the target Cloud SQL instance that the backup is '
            'restored to.'
        ),
    )
    parser.add_argument(
        '--backup-instance',
        completer=flags.InstanceCompleter,
        help=(
            'The ID of the instance that the backup was taken from. This'
            ' argument must be specified when the backup instance is different'
            ' from the restore instance. If it is not specified, the backup'
            ' instance is considered the same as the restore instance. This'
            ' flag is not supported when restore happens from backup name, only'
            ' supported when restore happens from backup ID in timestamp'
            ' format.'
        ),
    )
    parser.add_argument(
        '--backup-project',
        help=(
            'The project of the instance to which the backup belongs. If it'
            " isn't specified, backup and restore instances are in the same"
            ' project. This flag is not supported when restore happens from'
            ' backup name, only supported when restore happens from backup ID'
            ' in timestamp format.'
        ),
    )
    base.ASYNC_FLAG.AddToParser(parser)
    flags.AddSourceInstanceOverrideArgs(parser)

  def Run(self, args):
    """Restores a backup of a Cloud SQL instance.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
          with.

    Returns:
      A dict object representing the operations resource describing the
      restoreBackup operation if the restoreBackup was successful.
    """

    client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
    sql_client = client.sql_client
    sql_messages = client.sql_messages

    specified_args_dict = getattr(args, '_specified_args', None)
    overrides = [
        key
        for key in specified_args_dict
        if key in constants.TARGET_INSTANCE_OVERRIDE_FLAGS
    ]

    is_project_backup = command_validate.IsProjectLevelBackupRequest(args.id)
    _ValidateBackupRequest(is_project_backup, args, overrides)

    instance_ref = client.resource_parser.Parse(
        args.restore_instance,
        params={'project': properties.VALUES.core.project.GetOrFail},
        collection='sql.instances',
    )
    if not console_io.PromptContinue(
        '1. All current data on the instance will be lost when the backup is'
        ' restored to an existing instance.\n2. If restoring to a new instance,'
        ' settings will be applied from the backups unless they are overriden.'
    ):
      return None

    if is_project_backup:
      restore_backup_request = _GetRestoreBackupRequest(
          args, sql_messages, instance_ref
      )
      if overrides:
        instance_resource = (
            command_util.InstancesV1Beta4.ConstructCreateInstanceFromArgs(
                sql_messages, args, instance_ref=instance_ref
            )
        )
        restore_backup_request.instancesRestoreBackupRequest.restoreInstanceSettings = (
            instance_resource
        )
        restore_backup_request.instancesRestoreBackupRequest.restoreInstanceClearOverridesFieldNames = (
            _GetRestoreInstanceClearOverrides(args)
        )
      result_operation = sql_client.instances.RestoreBackup(
          restore_backup_request
      )
    else:
      if not args.backup_instance:
        args.backup_instance = args.restore_instance
      backup_run_id = int(args.id)
      result_operation = sql_client.instances.RestoreBackup(
          sql_messages.SqlInstancesRestoreBackupRequest(
              project=instance_ref.project,
              instance=instance_ref.instance,
              instancesRestoreBackupRequest=(
                  sql_messages.InstancesRestoreBackupRequest(
                      restoreBackupContext=sql_messages.RestoreBackupContext(
                          backupRunId=backup_run_id,
                          instanceId=args.backup_instance,
                          project=args.backup_project,
                      )
                  )
              ),
          )
      )

    operation_ref = client.resource_parser.Create(
        'sql.operations',
        operation=result_operation.name,
        project=instance_ref.project)

    if args.async_:
      return sql_client.operations.Get(
          sql_messages.SqlOperationsGetRequest(
              project=operation_ref.project,
              operation=operation_ref.operation))

    operations.OperationsV1Beta4.WaitForOperation(
        sql_client, operation_ref, 'Restoring Cloud SQL instance')

    log.status.write('Restored [{instance}].\n'.format(instance=instance_ref))

    return None
