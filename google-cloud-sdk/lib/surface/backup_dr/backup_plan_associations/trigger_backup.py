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
"""Create an on-demand backup."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.backupdr import util
from googlecloudsdk.api_lib.backupdr.backup_plan_associations import BackupPlanAssociationsClient
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class TriggerBackup(base.Command):
  """Create an on-demand backup for a resource."""

  detailed_help = {
      'BRIEF': 'Create an on-demand backup.',
      'DESCRIPTION': (
          '{description} Trigger an on demand backup for the given backup rule.'
      ),
      'EXAMPLES': """\
        To trigger an on demand backup for a backup plan association `sample-bpa` in project `sample-project` and location `us-central1` with backup rule `sample-backup-rule`, run:

          $ {command} sample-bpa --project=sample-project --location=us-central1 --backup-rule-id=sample-backup-rule
        """,
  }

  @staticmethod
  def Args(parser):
    """Specifies additional command flags.

    Args:
      parser: argparse.Parser: Parser object for command line inputs.
    """
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, True)
    flags.AddTriggerBackupFlags(parser)

  def Run(self, args):
    """Constructs and sends request.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      ProcessHttpResponse of the request made.
    """
    client = BackupPlanAssociationsClient()
    is_async = args.async_

    backup_plan_association = args.CONCEPTS.backup_plan_association.Parse()
    backup_rule = args.backup_rule_id
    custom_retention_days = args.custom_retention_days

    if backup_rule and custom_retention_days:
      raise calliope_exceptions.MutualExclusionError(
          'argument --custom-retention-days: At most one of --backup-rule-id |'
          ' --custom-retention-days may be specified.'
      )

    try:
      operation = client.TriggerBackup(
          backup_plan_association, backup_rule, custom_retention_days
      )
    except apitools_exceptions.HttpError as e:
      raise exceptions.HttpException(e, util.HTTP_ERROR_FORMAT)
    if is_async:
      # pylint: disable=protected-access
      # none of the log.CreatedResource, log.DeletedResource etc. matched
      log._PrintResourceChange(
          'on demand backup',
          backup_plan_association.RelativeName(),
          kind='backup plan association',
          is_async=True,
          details=util.ASYNC_OPERATION_MESSAGE.format(operation.name),
          failed=None,
      )
      return

    client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message=(
            'On demand backup in progress [{}]. (This operation usually takes'
            ' less than 15 minutes but could take up to 8 hours.)'.format(
                backup_plan_association.RelativeName()
            )
        ),
    )
    # pylint: disable=protected-access
    # none of the log.CreatedResource, log.DeletedResource etc. matched
    log._PrintResourceChange(
        'on demand backup',
        backup_plan_association.RelativeName(),
        kind='backup plan association',
        is_async=False,
        details=None,
        failed=None,
        operation_past_tense='on demand backup done for',
    )

    return
