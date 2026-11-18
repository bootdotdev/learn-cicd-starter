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
"""Updates Backup and DR Backup Plan Association."""

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


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  """Update a specific backup plan within a backup plan association."""

  detailed_help = {
      'BRIEF': (
          'Update a specific backup plan within a backup plan association.'
      ),
      'DESCRIPTION': (
          '{description}'
      ),
      'EXAMPLES': """\
        To update backup plan association `sample-bpa` in project `sample-project` and location `us-central1` with backup plan `sample-backup-plan` in the same project and location, run:

          $ {command} sample-bpa --project=sample-project --location=us-central1 --backup-plan=sample-backup-plan

        To update backup plan association `sample-bpa-uri` with backup plan `sample-backup-plan-uri` (using full URIs), run:

          $ {command} sample-bpa-uri --backup-plan=sample-backup-plan-uri

        To update backup plan association `sample-bpa` in location `us-central1` with backup plan `sample-backup-plan-uri`, run:

          $ {command} sample-bpa --location=us-central1 --backup-plan=sample-backup-plan-uri

        To update backup plan association `sample-bpa` in project `workload-project` and location `us-central1` with backup plan `sample-backup-plan` in project `sample-project`, run:

          $ {command} sample-bpa --workload-project=workload-project --location=us-central1 --backup-plan=sample-backup-plan --project=sample-project
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
    flags.AddUpdateBackupPlanAssociationFlags(parser)

  def GetUpdateMask(self, args):
    return 'backup_plan' if args.IsSpecified('backup_plan') else ''

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
    backup_plan = args.CONCEPTS.backup_plan.Parse()

    try:
      parsed_bpa = client.ParseUpdate(backup_plan)
      update_mask = self.GetUpdateMask(args)
      operation = client.Update(
          backup_plan_association,
          parsed_bpa,
          update_mask=update_mask,
      )
    except apitools_exceptions.HttpError as e:
      raise exceptions.HttpException(e, util.HTTP_ERROR_FORMAT) from e

    if is_async:
      log.UpdatedResource(
          backup_plan_association.RelativeName(),
          kind='backup plan association',
          is_async=True,
          details=util.ASYNC_OPERATION_MESSAGE.format(operation.name),
      )
      return operation

    resource = client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message=(
            'Updating backup plan association [{}].  (This operation could'
            ' take up to 2 minutes.)'.format(
                backup_plan_association.RelativeName()
            )
        ),
    )
    log.UpdatedResource(
        backup_plan_association.RelativeName(), kind='backup plan association'
    )
    return resource
