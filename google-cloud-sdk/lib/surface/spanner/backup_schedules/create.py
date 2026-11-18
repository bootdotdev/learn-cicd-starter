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
"""Command for spanner backup schedule create."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.spanner import backup_schedules
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.spanner import resource_args


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Create(base.CreateCommand):
  """Create a Cloud Spanner backup schedule."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
        To create a Cloud Spanner backup schedule, run:

          $ {command} backup-schedule-id --instance=instance-id --database=database-id --cron="0 2 * * *" --retention-duration=2w --backup-type=full-backup
        """),
  }

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Please add arguments in alphabetical order except for no- or a clear- pair
    for that argument which can follow the argument itself.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    resource_args.AddBackupScheduleResourceArg(parser, 'to create')
    backup_type_choices = ['full-backup', 'incremental-backup']
    parser.add_argument(
        '--backup-type',
        metavar='BACKUP_TYPE',
        required=True,
        help=("""\
Type of backups created by this schedule.

Supported backup types:

`full-backup`
  A full backup stores the entire contents of the database at a given version time.

`incremental-backup`
  An incremental backup contains only the data that has changed since a previous backup.
"""),
        type=arg_parsers.ArgList(
            choices=backup_type_choices,
            max_length=1,
        ),
    )
    parser.add_argument(
        '--cron',
        required=True,
        help=(
            'Textual representation of the crontab. User can customize the'
            ' backup frequency and the backup version time using the cron'
            ' expression. The version time must be in UTC timzeone. The backup'
            ' will contain an externally consistent copy of the database at the'
            ' version time. Allowed frequencies are 12 hour, 1 day, 1 week and'
            ' 1 month. Examples of valid cron specifications: * `0 2/12 * * * `'
            ' : every 12 hours at (2, 14) hours past midnight in UTC. * `0 2,14'
            ' * * * ` : every 12 hours at (2,14) hours past midnight in UTC. *'
            ' `0 2 * * * ` : once a day at 2 past midnight in UTC. * `0 2 * * 0'
            ' ` : once a week every Sunday at 2 past midnight in UTC. * `0 2 8'
            ' * * ` : once a month on 8th day at 2 past midnight in UTC.'
        ),
    )
    parser.add_argument(
        '--retention-duration',
        required=True,
        help=(
            'The retention duration of a backup that must be at least 6 hours'
            ' and at most 366 days. The backup is eligible to be automatically'
            ' deleted once the retention period has elapsed.'
        ),
    )
    encryption_group_parser = parser.add_argument_group()
    resource_args.AddCreateBackupEncryptionConfigTypeArg(
        encryption_group_parser
    )
    resource_args.AddKmsKeyResourceArg(
        encryption_group_parser, 'to create the Cloud Spanner backup'
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    backup_schedule_ref = args.CONCEPTS.backup_schedule.Parse()
    encryption_type = resource_args.GetCreateBackupEncryptionConfigType(args)
    kms_key = resource_args.GetAndValidateKmsKeyName(args)
    return backup_schedules.Create(
        backup_schedule_ref, args, encryption_type, kms_key
    )
