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
"""Delete a specified Backup and DR Backup Plan Association."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.backupdr import util
from googlecloudsdk.api_lib.backupdr.backup_plan_associations import BackupPlanAssociationsClient
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Delete(base.DeleteCommand):
  """Delete the specified backup plan association."""

  detailed_help = {
      'BRIEF': 'Delete a specific backup plan association',
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
        To delete a backup plan association `sample-bpa` in project `sample-project` and location `us-central1` , run:

          $ {command} sample-bpa --project=sample-project --location=us-central1
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
    flags.AddBackupPlanAssociationResourceArg(
        parser,
        'Name of the backup plan association to delete.',
    )

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

    console_io.PromptContinue(
        message=(
            'The backup plan association will be deleted. You cannot undo this'
            ' action.'
        ),
        default=True,
        cancel_on_no=True,
    )

    try:
      operation = client.Delete(backup_plan_association)
    except apitools_exceptions.HttpError as e:
      raise exceptions.HttpException(e, util.HTTP_ERROR_FORMAT)
    if is_async:
      log.DeletedResource(
          backup_plan_association.RelativeName(),
          kind='backup plan association',
          is_async=True,
          details=util.ASYNC_OPERATION_MESSAGE.format(operation.name),
      )
      return operation

    response = client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message=(
            'Deleting backup plan association [{}]. (This operation could'
            ' take up to 2 minutes.)'.format(
                backup_plan_association.RelativeName()
            )
        ),
        has_result=False,
    )
    log.DeletedResource(
        backup_plan_association.RelativeName(), kind='backup plan association'
    )

    return response
