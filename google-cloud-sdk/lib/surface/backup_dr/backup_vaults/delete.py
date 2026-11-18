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
"""Deletes a Backup and DR Backup Vault."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.backupdr import util
from googlecloudsdk.api_lib.backupdr.backup_vaults import BackupVaultsClient
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Delete(base.DeleteCommand):
  """Delete the specified Backup Vault."""

  detailed_help = {
      'BRIEF': 'Deletes a specific backup vault',
      'DESCRIPTION': '{description}',
      'API REFERENCE': (
          'This command uses the backupdr/v1 API. The full documentation for'
          ' this API can be found at:'
          ' https://cloud.google.com/backup-disaster-recovery'
      ),
      'EXAMPLES': """\
        To delete a backup vault ``BACKUP_VAULT'' in location ``MY_LOCATION'', run:

        $ {command} BACKUP_VAULT --location=MY_LOCATION

        To override restrictions against the deletion of a backup vault ``BACKUP_VAULT''
        containing inactive datasources in location ``MY_LOCATION'', run:

        $ {command} BACKUP_VAULT --location=MY_LOCATION --ignore-inactive-datasources

        To override restrictions against the deletion of a backup vault ``BACKUP_VAULT''
        containing backup plan references in location ``MY_LOCATION'', run:

        $ {command} BACKUP_VAULT --location=MY_LOCATION --ignore-backup-plan-references
        """,
  }

  @staticmethod
  def Args(parser):
    """Specifies additional command flags.

    Args:
      parser: argparse.Parser: Parser object for command line inputs.
    """
    flags.AddBackupVaultResourceArg(
        parser,
        'Name of the backup vault to delete. Before you delete, take a look at'
        ' the prerequisites'
        ' [here](https://cloud.google.com/backup-disaster-recovery/docs/configuration/decommission).',
    )
    flags.AddNoAsyncFlag(parser)
    flags.AddIgnoreInactiveDatasourcesFlag(parser)
    flags.AddIgnoreBackupPlanReferencesFlag(parser)
    flags.AddAllowMissing(parser, 'backup vault')

  def Run(self, args):
    """Constructs and sends request.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      ProcessHttpResponse of the request made.
    """
    client = BackupVaultsClient()
    backup_vault = args.CONCEPTS.backup_vault.Parse()
    no_async = args.no_async

    console_io.PromptContinue(
        message=(
            'The backup vault will be deleted. You cannot undo this action.'
        ),
        default=True,
        cancel_on_no=True,
    )

    try:
      operation = client.Delete(
          backup_vault,
          ignore_inactive_datasources=args.ignore_inactive_datasources,
          ignore_backup_plan_references=args.ignore_backup_plan_references,
          allow_missing=args.allow_missing,
      )
    except apitools_exceptions.HttpError as e:
      raise exceptions.HttpException(e, util.HTTP_ERROR_FORMAT)

    operation_ref = client.GetOperationRef(operation)
    if args.allow_missing and operation_ref == 'None':
      log.DeletedResource(
          operation.name,
          kind='backup vault',
          is_async=False,
          details=(
              '= requested backup vault [{}] was not found.'.format(
                  backup_vault.RelativeName()
              )
          ),
      )
      return operation

    if no_async:
      return client.WaitForOperation(
          operation_ref=operation_ref,
          message=(
              'Deleting backup vault [{}]. (This operation could'
              ' take up to 2 minutes.)'.format(backup_vault.RelativeName())
          ),
          has_result=False,
      )

    log.DeletedResource(
        backup_vault.RelativeName(),
        kind='backup vault',
        is_async=True,
        details=util.ASYNC_OPERATION_MESSAGE.format(operation.name),
    )
    return operation
