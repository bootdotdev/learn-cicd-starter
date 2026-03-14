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
"""Updates a Backup and DR Backup Vault."""

import argparse

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.backupdr import util
from googlecloudsdk.api_lib.backupdr.backup_vaults import BackupVaultsClient
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.command_lib.backupdr import util as command_util
from googlecloudsdk.core import log


def _add_common_args(parser: argparse.ArgumentParser):
  """Specifies additional command flags.

  Args:
    parser: argparse.Parser: Parser object for command line inputs.
  """
  flags.AddBackupVaultResourceArg(
      parser,
      'Name of the existing backup vault to update.',
  )
  flags.AddNoAsyncFlag(parser)
  flags.AddEnforcedRetention(parser, False)
  flags.AddDescription(parser)
  flags.AddEffectiveTime(parser)
  flags.AddUnlockBackupMinEnforcedRetention(parser)
  flags.AddForceUpdateFlag(parser)
  flags.AddForceUpdateAccessRestriction(parser)
  flags.AddBackupVaultAccessRestrictionEnumFlag(parser, 'update')


def _add_common_update_mask(args: argparse.Namespace) -> str:
  """Creates the update mask for the update command.

  Args:
    args: argparse.Namespace, An object that contains the values for the
      arguments specified in the .Args() method.

  Returns:
    A string containing the update mask.
  """
  updated_fields = []
  if args.IsSpecified('description'):
    updated_fields.append('description')
  if args.IsSpecified('backup_min_enforced_retention'):
    updated_fields.append('backupMinimumEnforcedRetentionDuration')
  if args.IsSpecified(
      'unlock_backup_min_enforced_retention'
  ) or args.IsSpecified('effective_time'):
    updated_fields.append('effectiveTime')
  if args.IsSpecified('access_restriction'):
    updated_fields.append('accessRestriction')
  return ','.join(updated_fields)


def _parse_update_bv(args: argparse.Namespace):
  """Parses the update backup vault arguments.

  Args:
    args: argparse.Namespace, An object that contains the values for the
      arguments specified in the .Args() method.

  Returns:
    A tuple containing the backup min enforced retention, description and
    effective time.

  Raises:
    calliope_exceptions.ConflictingArgumentsException: If both
      --unlock-backup-min-enforced-retention and --effective-time are specified.
  """
  backup_min_enforced_retention = command_util.ConvertIntToStr(
      args.backup_min_enforced_retention
  )
  description = args.description

  if args.unlock_backup_min_enforced_retention and args.effective_time:
    raise calliope_exceptions.ConflictingArgumentsException(
        'Only one of --unlock-backup-min-enforced-retention or '
        '--effective-time can be specified.'
    )

  if args.unlock_backup_min_enforced_retention:
    effective_time = command_util.ResetEnforcedRetention()
  else:
    effective_time = command_util.VerifyDateInFuture(
        args.effective_time, 'effective-time'
    )
  if args.access_restriction:
    access_restriction = args.access_restriction
  else:
    access_restriction = None

  return (
      backup_min_enforced_retention,
      description,
      effective_time,
      access_restriction,
  )


def _run(
    self,
    args: argparse.Namespace,
):
  """Constructs and sends request.

  Args:
    self: The object that is calling this method.
    args: argparse.Namespace, An object that contains the values for the
      arguments specified in the .Args() method.

  Returns:
    ProcessHttpResponse of the request made.

  Raises:
    exceptions.HttpException: if the http request fails.
  """
  client = BackupVaultsClient()
  backup_vault = args.CONCEPTS.backup_vault.Parse()
  no_async = args.no_async
  force_update_access_restriction = args.force_update_access_restriction

  try:
    parsed_bv = self.ParseUpdateBv(args, client)

    update_mask = self.GetUpdateMask(args)

    operation = client.Update(
        backup_vault,
        parsed_bv,
        force_update=args.force_update,
        update_mask=update_mask,
        force_update_access_restriction=force_update_access_restriction,
    )

  except apitools_exceptions.HttpError as e:
    raise exceptions.HttpException(e, util.HTTP_ERROR_FORMAT)

  if no_async:
    resource = client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message=(
            'Updating backup vault [{}]. (This operation could'
            ' take up to 1 minute.)'.format(backup_vault.RelativeName())
        ),
        has_result=False,
    )
    log.UpdatedResource(backup_vault.RelativeName(), kind='backup vault')
    return resource

  log.UpdatedResource(
      backup_vault.RelativeName(),
      kind='backup vault',
      is_async=True,
      details=util.ASYNC_OPERATION_MESSAGE.format(operation.name),
  )
  return operation


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Update(base.UpdateCommand):
  """Update a Backup and DR backup vault."""

  detailed_help = {
      'BRIEF': 'Updates a Backup and DR backup vault.',
      'DESCRIPTION': '{description}',
      'API REFERENCE': (
          'This command uses the backupdr/v1 API. The full documentation for'
          ' this API can be found at:'
          ' https://cloud.google.com/backup-disaster-recovery'
      ),
      'EXAMPLES': """\
        To update a backup vault BACKUP_VAULT in location MY_LOCATION with one update
        field, run:

        $ {command} BACKUP_VAULT --location=MY_LOCATION --effective-time="2024-03-22"

        To update a backup vault BACKUP_VAULT in location MY_LOCATION with multiple
        update fields, run:

        $ {command} BACKUP_VAULT --location=MY_LOCATION \
            --backup-min-enforced-retention="400000s" --description="Updated backup vault"
        """,
  }

  @staticmethod
  def Args(parser: argparse.ArgumentParser):
    """Specifies additional command flags.

    Args:
      parser: argparse.Parser: Parser object for command line inputs.
    """
    _add_common_args(parser)

  def GetUpdateMask(self, args: argparse.Namespace) -> str:
    """Returns the update mask for the update command.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      A string containing the update mask.
    """
    return _add_common_update_mask(args)

  def ParseUpdateBv(self, args: argparse.Namespace, client: BackupVaultsClient):
    """Parses the update backup vault arguments.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.
      client: BackupVaultsClient, The client to use to parse the backup vault.

    Returns:
      A parsed backup vault object.
    """
    (
        backup_min_enforced_retention,
        description,
        effective_time,
        access_restriction,
    ) = _parse_update_bv(args)

    return client.ParseUpdate(
        description=description,
        backup_min_enforced_retention=backup_min_enforced_retention,
        effective_time=effective_time,
        access_restriction=access_restriction,
    )

  def Run(self, args):
    return _run(self, args)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(Update):
  """Update a Backup and DR backup vault."""

  @staticmethod
  def Args(parser):
    """Specifies additional command flags.

    Args:
      parser: argparse.Parser: Parser object for command line inputs.
    """
    _add_common_args(parser)

  def ParseUpdateBv(self, args: argparse.Namespace, client: BackupVaultsClient):
    """Parses the update backup vault arguments.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.
      client: BackupVaultsClient, The client to use to parse the backup vault.

    Returns:
      A parsed backup vault object.
    """
    (
        backup_min_enforced_retention,
        description,
        effective_time,
        access_restriction,
    ) = _parse_update_bv(args)

    return client.ParseUpdate(
        description=description,
        backup_min_enforced_retention=backup_min_enforced_retention,
        effective_time=effective_time,
        access_restriction=access_restriction,
    )

  def GetUpdateMask(self, args: argparse.Namespace) -> str:
    """Returns the update mask for the update command.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      A string containing the update mask.
    """
    mask = _add_common_update_mask(args)
    return mask

  def Run(self, args):
    return _run(self, args)
