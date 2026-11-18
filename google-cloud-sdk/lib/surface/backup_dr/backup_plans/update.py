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
"""Updates a new Backup Plan."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.backupdr import backup_plans
from googlecloudsdk.api_lib.backupdr import util
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.core import exceptions as core_exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import yaml


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  """Update a specific backup plan."""

  detailed_help = {
      'BRIEF': 'Update a specific backup plan',
      'DESCRIPTION': """\
          Update a specific backup plan in the project. It can only be updated in regions supported by the Backup and DR Service.
      """,
      'EXAMPLES': """\
        To update 2 backup rules and description of an existing backup plan ``sample-backup-plan''
        in project ``sample-project'',
        at location ``us-central1'':

        run:

          $ {command} sample-backup-plan --project=sample-project --location=us-central1
            --backup-rule <BACKUP-RULE>
            --backup-rule <BACKUP-RULE>
            --description "This is a sample backup plan"

        To add backup rules to an existing backup plan ``sample-backup-plan''
        in project ``sample-project'',
        at location ``us-central1'':

        run:

          $ {command} sample-backup-plan --project=sample-project --location=us-central1
            --add-backup-rule <BACKUP-RULE>
            --add-backup-rule <BACKUP-RULE>

        To remove a backup rule with id ``sample-daily-rule'' from an existing backup plan ``sample-backup-plan''
        in project ``sample-project'',
        at location ``us-central1'':

        run:

          $ {command} sample-backup-plan --project=sample-project --location=us-central1
            --remove-backup-rule sample-daily-rule

        To override backup rules in an existing backup plan ``sample-backup-plan''
        in project ``sample-project'',
        at location ``us-central1'', pass a file path containing backup rules in YAML or JSON format:
        This flag is mutually exclusive with --add-backup-rule, --remove-backup-rule and --backup-rule flags.

        run:
          $ {command} sample-backup-plan --project=sample-project --location=us-central1
            --backup-rules-fom-file <FILE_PATH>

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

        YAML and JSON file examples:

        YAML file example:

        ```
        backup-rules:
        - rule-id: weekly-rule
          retention-days: 7
          recurrence: WEEKLY
          backup-window-start: 0
          backup-window-end: 23
          days-of-week: [MONDAY, TUESDAY]
          time-zone: UTC
        - rule-id: daily-rule
          retention-days: 1
          recurrence: DAILY
          backup-window-start: 1
          backup-window-end: 24
          time-zone: UTC
        ```

        JSON file example:
        ```
        {
          "backup-rules": [
            {
              "rule-id": "weekly-rule",
              "retention-days": 7,
              "recurrence": "WEEKLY",
              "backup-window-start": 0,
              "backup-window-end": 23,
              "days-of-week": ["MONDAY", "TUESDAY"],
              "time-zone": "UTC"
            },
            {
              "rule-id": "daily-rule",
              "retention-days": 1,
              "recurrence": "DAILY",
              "backup-window-start": 1,
              "backup-window-end": 24,
              "time-zone": "UTC"
            }
          ]
        }
        ```
        """,
  }

  @staticmethod
  def Args(parser: argparse.ArgumentParser):
    """Specifies additional command flags.

    Args:
      parser: Parser object for command line inputs.
    """
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, True)
    flags.AddBackupPlanResourceArg(
        parser,
        """Name of the backup plan to be updated.
        The name must be unique for a project and location.
        """,
    )
    flags.AddUpdateBackupRule(parser)
    flags.AddAddBackupRule(parser)
    flags.AddRemoveBackupRule(parser)
    flags.AddBackupRulesFromFile(parser)

    description_help = """\
        Provide a description of the backup plan, such as specific use cases and
        relevant details, in 2048 characters or less.

        E.g., This is a backup plan that performs a daily backup at 6 p.m. and
        retains data for 3 months.
        """
    flags.AddDescription(parser, description_help)
    flags.AddLogRetentionDays(parser)
    flags.AddMaxCustomOnDemandRetentionDays(parser)

  class YamlOrJsonLoadError(core_exceptions.Error):
    """Error parsing YAML or JSON file content."""

  def _GetBackupRulesFromFile(self, backup_rules_file_content):
    """Parses the backup rules from the file content."""
    try:
      backup_rules = yaml.load(backup_rules_file_content)
      return backup_rules.get('backup-rules')
    except Exception as exc:  # pylint: disable=broad-except
      raise self.YamlOrJsonLoadError(
          'Could not parse content in the backup rules file: {0}'.format(exc)
      ) from exc

  def Run(self, args) -> any:
    """Constructs and sends request.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      ProcessHttpResponse of the request made.
    """
    client = backup_plans.BackupPlansClient()

    backup_plan = args.CONCEPTS.backup_plan.Parse()
    backup_rules_file_content = args.backup_rules_from_file
    update_backup_rules = args.backup_rule
    add_backup_rules = args.add_backup_rule
    remove_backup_rules = args.remove_backup_rule

    if backup_rules_file_content and (
        update_backup_rules or add_backup_rules or remove_backup_rules
    ):
      raise core_exceptions.Error(
          '--backup-rules-from-file flag cannot be used with'
          ' --backup-rule, --add-backup-rule or --remove-backup-rule flags.'
      )

    log_retention_days = args.log_retention_days
    description = args.description
    max_custom_on_demand_retention_days = (
        args.max_custom_on_demand_retention_days
    )

    try:
      current_backup_plan = client.Describe(backup_plan)
      new_backup_rules_from_file = None
      if backup_rules_file_content:
        new_backup_rules_from_file = self._GetBackupRulesFromFile(
            backup_rules_file_content
        )
      updated_backup_plan = client.ParseUpdate(
          description,
          new_backup_rules_from_file,
          update_backup_rules,
          add_backup_rules,
          remove_backup_rules,
          current_backup_plan,
          log_retention_days,
          max_custom_on_demand_retention_days,
      )
      update_mask = []
      if (
          description is not None
          and description != current_backup_plan.description
      ):
        update_mask.append('description')
      if (
          log_retention_days is not None
          and log_retention_days != current_backup_plan.logRetentionDays
      ):
        update_mask.append('logRetentionDays')
      if (
          max_custom_on_demand_retention_days is not None
          and max_custom_on_demand_retention_days
          != current_backup_plan.maxCustomOnDemandRetentionDays
      ):
        update_mask.append('maxCustomOnDemandRetentionDays')
      if any([
          update_backup_rules,
          add_backup_rules,
          remove_backup_rules,
          new_backup_rules_from_file,
      ]):
        update_mask.append('backupRules')
      operation = client.Update(
          backup_plan, updated_backup_plan, ','.join(update_mask)
      )
    except apitools_exceptions.HttpError as e:
      raise exceptions.HttpException(e, util.HTTP_ERROR_FORMAT)

    if args.async_:
      log.UpdatedResource(
          backup_plan.RelativeName(),
          kind='backup plan',
          is_async=True,
          details=util.ASYNC_OPERATION_MESSAGE.format(operation.name),
      )
      return operation

    resource = client.WaitForOperation(
        operation_ref=client.GetOperationRef(operation),
        message=(
            f'Updating backup plan [{backup_plan.RelativeName()}]. (This'
            ' operation could take up to 2 minutes.)'
        ),
    )
    log.UpdatedResource(backup_plan.RelativeName(), kind='backup plan')

    return resource
