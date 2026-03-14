# -*- coding: utf-8 -*- #
# Copyright 2024 Google Inc. All Rights Reserved.
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
"""Create command for Backup for GKE backup."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.container.backup_restore import util as api_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.backup_restore import resource_args

@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)


class GetBackupIndexDownloadUrl(base.Command):
  """Get a backup index download URL.

  Get backup index download URL for a Backup for GKE backup. Backup index
  displays resources' basic information stored in the backup.

  ## EXAMPLES

  To get the backup index associated with a backup ``my-backup'' in backup plan
  ``my-backup-plan'' in project ``my-project'' in location ``us-central1'', run:

    $ {command} my-backup --project=my-project --location=us-central1
    --backup-plan=my-backup-plan
  """

  @staticmethod
  def Args(parser):
    resource_args.AddBackupArg(parser)

  def Run(self, args):
    backup_ref = args.CONCEPTS.backup.Parse()
    return api_util.GetBackupIndexDownloadUrl(backup_ref)
