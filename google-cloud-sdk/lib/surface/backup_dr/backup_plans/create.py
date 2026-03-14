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
"""Creates a new Backup Plan."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.backupdr import backup_plans
from googlecloudsdk.api_lib.backupdr import util
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Create(base.CreateCommand):
  """Creates a new Backup Plan."""

  detailed_help = {
      'BRIEF': 'Creates a new backup plan',
      'DESCRIPTION': """\
          Create a new backup plan in the project. It can only be created in
          locations where Backup and DR is available.
      """,
      'EXAMPLES': """\
        To create a new backup plan ``sample-backup-plan''
        in project ``sample-project'',
        at location ``us-central1'',
        with resource-type ``compute.<UNIVERSE_DOMAIN>.com/Instance'' and
        backup-vault ``backup-vault''
        with 2 backup-rules:

        run:

          $ {command} sample-backup-plan --project=sample-project --location=us-central1
            --resource-type 'compute.<UNIVERSE_DOMAIN>.com/Instance'
            --backup-vault <BACKUP-VAULT>
            --backup-rule <BACKUP-RULE>
            --backup-rule <BACKUP-RULE>

        Backup Rule Examples:

        1. Hourly backup rule with hourly backup frequency of 6 hours and store it for 30 days, and expect the backups to run only between 10:00 to 20:00 UTC

        <BACKUP-RULE>: rule-id=sample-hourly-rule,retention-days=30,recurrence=HOURLY,hourly-frequency=6,time-zone=UTC,backup-window-start=10,backup-window-end=20

        Properties:
          -- rule-id = "sample-hourly-rule"
          -- retention-days = 30
          -- recurrence = HOURLY
          -- hourly-frequency = 6
          -- time-zone = UTC
          -- backup-window-start = 10
          -- backup-window-end = 20

        2. Daily backup rule with daily backup frequency of 6 hours and store it for 7 days

        <BACKUP-RULE>: rule-id=sample-daily-rule,retention-days=7,recurrence=DAILY,backup-window-start=1,backup-window-end=14

        Properties:
          -- rule-id = "sample-daily-rule"
          -- retention-days = 7
          -- recurrence = DAILY
          -- backup-window-start = 1
          -- backup-window-end = 14

        3. Weekly backup rule with weekly backup frequency on every MONDAY & FRIDAY and store it for 21 days

        <BACKUP-RULE>: rule-id=sample-weekly-rule,retention-days=21,recurrence=WEEKLY,days-of-week="MONDAY FRIDAY",backup-window-start=10,backup-window-end=20

        Properties:
          -- rule-id = "sample-weekly-rule"
          -- retention-days: 21
          -- recurrence = WEEKLY
          -- days-of-week = "MONDAY FRIDAY"
          -- backup-window-start = 10
          -- backup-window-end = 20
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
    flags.AddBackupPlanResourceArgWithBackupVault(
        parser,
        """Name of the backup plan to be created.
        Once the backup plan is created, this name can't be changed.
        The name must be unique for a project and location.
        """,
    )
    flags.AddResourceType(
        parser,
        """Type of resource to which the backup plan should be applied.
          E.g., `compute.<UNIVERSE_DOMAIN>.com/Instance` """,
    )
    flags.AddBackupRule(parser)
    flags.AddMaxCustomOnDemandRetentionDays(parser)

    description_help = """\
        Provide a description of the backup plan, such as specific use cases and
        relevant details, in 2048 characters or less.

        E.g., This is a backup plan that performs a daily backup at 6 p.m. and
        retains data for 3 months.
        """
    flags.AddDescription(parser, description_help)

    labels_help = """\
        If you have assigned labels to your resources for grouping, you can
        provide the label using this flag.A label is a key-value pair.

        Keys must start with a lowercase character and contain only hyphens (-),
        underscores (_), lowercase characters, and numbers. Values must contain
        only hyphens (-), underscores (_), lowercase characters, and numbers.
        """
    flags.AddLabels(parser, labels_help)
    flags.AddLogRetentionDays(parser)

  def Run(self, args):
    """Constructs and sends request.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      ProcessHttpResponse of the request made.
    """
    client = backup_plans.BackupPlansClient()
    is_async = args.async_

    backup_plan = args.CONCEPTS.backup_plan.Parse()
    backup_vault = args.CONCEPTS.backup_vault.Parse()
    resource_type = args.resource_type
    backup_rules = args.backup_rule
    log_retention_days = args.log_retention_days
    description = args.description
    labels = args.labels
    max_custom_on_demand_retention_days = (
        args.max_custom_on_demand_retention_days
    )

    try:
      operation = client.Create(
          backup_plan,
          backup_vault.RelativeName(),
          resource_type,
          backup_rules,
          log_retention_days,
          description,
          labels,
          max_custom_on_demand_retention_days
      )
    except apitools_exceptions.HttpError as e:
      raise exceptions.HttpException(e, util.HTTP_ERROR_FORMAT)

    if is_async:
      log.CreatedResource(
          backup_plan.RelativeName(),
          kind='backup plan',
          is_async=True,
          details=util.ASYNC_OPERATION_MESSAGE.format(operation.name),
      )
      return operation

    resource = client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message=(
            'Creating backup plan [{}]. (This operation could'
            ' take up to 2 minutes.)'.format(backup_plan.RelativeName())
        ),
    )
    log.CreatedResource(backup_plan.RelativeName(), kind='backup plan')

    return resource
