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
"""Command for spanner backup schedule list."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.spanner import backup_schedules
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.spanner import resource_args


def _TransformBackupTypeSpec(schedule):
  """Transforms the backup type spec field to a human readable string."""
  if 'fullBackupSpec' in schedule:
    return 'FULL'
  elif 'incrementalBackupSpec' in schedule:
    return 'INCREMENTAL'
  # This should never happen.
  return 'UNSPECIFIED'


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class List(base.ListCommand):
  """List Cloud Spanner backup schedules."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
        To list Cloud Spanner backup schedules, run:

          $ {command} --instance=instance-id --database=database-id
        """),
  }

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Please add arguments in alphabetical order except for no- or a clear- pair
    for that argument which can follow the argument itself.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command.
    """
    resource_args.AddDatabaseResourceArg(
        parser, 'in which to list schedules', positional=False)
    parser.display_info.AddFormat("""
          table(
            name.basename(),
            backup_type_spec():label=BACKUP_TYPE,
            spec.cronSpec.text:label=CRON,
            retentionDuration,
            encryptionConfig.encryptionType,
            encryptionConfig.kmsKeyName,
            encryptionConfig.kmsKeyNames
          )
        """)
    parser.display_info.AddTransforms({
        'backup_type_spec': _TransformBackupTypeSpec,
    })

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    return backup_schedules.List(args.CONCEPTS.database.Parse())
