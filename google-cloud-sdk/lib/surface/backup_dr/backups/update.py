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
"""Updates a Backup and DR Backup."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.backupdr import util
from googlecloudsdk.api_lib.backupdr.backups import BackupsClient
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.command_lib.backupdr import util as command_util
from googlecloudsdk.core import log


def _add_common_args(parser: argparse.ArgumentParser):
  """Specifies additional command flags.

  Args:
    parser: argparse.Parser: Parser object for command line inputs.
  """
  base.ASYNC_FLAG.AddToParser(parser)
  base.ASYNC_FLAG.SetDefault(parser, True)
  flags.AddBackupResourceArg(
      parser,
      'Name of the backup to update.',
  )
  flags.AddUpdateBackupFlags(parser)


def _add_common_update_mask(args) -> str:
  updated_fields = []
  if args.IsSpecified('enforced_retention_end_time'):
    updated_fields.append('enforcedRetentionEndTime')
  if args.IsSpecified('expire_time'):
    updated_fields.append('expireTime')
  return ','.join(updated_fields)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  """Update the specified Backup."""

  detailed_help = {
      'BRIEF': 'Updates a specific backup',
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
        To update the enforced retention of a backup sample-backup in backup vault sample-vault, data source
        sample-ds, project sample-project and location us-central1, run:

          $ {command} sample-backup --backup-vault=sample-vault --data-source=sample-ds --project=sample-project --location=us-central1 --enforced-retention-end-time="2025-02-14T01:10:20Z"
        """,
  }

  @staticmethod
  def Args(parser: argparse.ArgumentParser):
    _add_common_args(parser)

  def ParseUpdate(self, args, client):
    updated_enforced_retention = command_util.VerifyDateInFuture(
        args.enforced_retention_end_time, 'enforced-retention-end-time'
    )

    expire_time = command_util.VerifyDateInFuture(
        args.expire_time, 'expire-time'
    )

    parsed_backup = client.ParseUpdate(updated_enforced_retention, expire_time)

    return parsed_backup

  def GetUpdateMask(self, args):
    return _add_common_update_mask(args)

  def Run(self, args):
    """Constructs and sends request.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      ProcessHttpResponse of the request made.
    """
    client = BackupsClient()
    is_async = args.async_
    backup = args.CONCEPTS.backup.Parse()
    try:
      parsed_backup = self.ParseUpdate(args, client)

      update_mask = self.GetUpdateMask(args)

      operation = client.Update(
          backup,
          parsed_backup,
          update_mask=update_mask,
      )
    except apitools_exceptions.HttpError as e:
      raise exceptions.HttpException(e, util.HTTP_ERROR_FORMAT)

    if is_async:
      log.UpdatedResource(
          backup.RelativeName(),
          kind='backup',
          is_async=True,
          details=util.ASYNC_OPERATION_MESSAGE.format(operation.name),
      )
      return operation

    response = client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message=(
            'Updating backup [{}]. (This operation usually takes less than 1'
            ' minute.)'.format(backup.RelativeName())
        ),
        has_result=False,
    )
    log.UpdatedResource(backup.RelativeName(), kind='backup')

    return response


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(Update):
  """Update the specified Backup."""

  @staticmethod
  def Args(parser: argparse.ArgumentParser):
    _add_common_args(parser)

  def ParseUpdate(self, args, client):
    updated_enforced_retention = command_util.VerifyDateInFuture(
        args.enforced_retention_end_time, 'enforced-retention-end-time'
    )

    expire_time = command_util.VerifyDateInFuture(
        args.expire_time, 'expire-time'
    )

    parsed_backup = client.ParseUpdate(updated_enforced_retention, expire_time)

    return parsed_backup

  def GetUpdateMask(self, args):
    return _add_common_update_mask(args)
