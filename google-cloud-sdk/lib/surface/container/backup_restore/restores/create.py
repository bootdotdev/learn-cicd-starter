# -*- coding: utf-8 -*- #
# Copyright 2021 Google Inc. All Rights Reserved.
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
"""Create command for Backup for GKE restore."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.container.backup_restore import util as api_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.backup_restore import hooks
from googlecloudsdk.command_lib.container.backup_restore import resource_args
from googlecloudsdk.command_lib.util.args import labels_util


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Create(base.CreateCommand):
  """Creates a restore.

  Creates a Backup for GKE restore.

  ## EXAMPLES

  To create a restore ``my-restore'' in location ``us-central1'' under restore
  plan ``my-restore-plan'', run:

    $ {command} my-restore --project=my-project --location=us-central1
    --restore-plan=my-restore-plan
    --backup=projects/my-project/locations/us-east1/backupPlans/my-backup-plan/backups/my-backup
  """

  @staticmethod
  def Args(parser):
    resource_args.AddRestoreArg(parser)
    group = parser.add_group(mutex=True)
    group.add_argument(
        '--async',
        required=False,
        action='store_true',
        default=False,
        help="""
        Return immediately, without waiting for the operation in progress to
        complete.
        """,
    )
    group.add_argument(
        '--wait-for-completion',
        required=False,
        action='store_true',
        default=False,
        help='Wait for the created restore to complete.',
    )
    # TODO(b/205222596): Figure out if we can/should use the relative name of
    # the backup. This would potentially require the CLI to first get the backup
    # plan referenced in the parent restore plan and then concat it with the
    # user input relative name.
    parser.add_argument(
        '--backup',
        type=str,
        required=True,
        help="""
        Name of the backup from which to restore under the backup plan specified
        in restore plan.
        Format: projects/<project>/locations/<location>/backupPlans/<backupPlan>/backups/<backup>.
        """,
    )
    parser.add_argument(
        '--description',
        type=str,
        required=False,
        default=None,
        help='Optional text description for the restore.',
    )
    parser.add_argument(
        '--volume-data-restore-policy-overrides-file',
        required=False,
        default=None,
        help="""
        If provided, defines an array of volume data restore policy overrides
        from the given config file in yaml.
        """,
    )
    parser.add_argument(
        '--filter-file',
        required=False,
        default=None,
        help="""
        JSON/YAML file containing the configuration of the fine-grained
        restore filter which can be used to further refine the resource
        selection of the Restore beyond the coarse-grained scope defined
        in the RestorePlan.

        For more information about examples and how to use this filter,
        please refer to the Backup for GKE documentation:
        https://cloud.google.com/kubernetes-engine/docs/add-on/backup-for-gke/how-to/fine-grained-restore.
        """,
    )
    labels_util.AddCreateLabelsFlags(parser)

  def Run(self, args):
    labels = labels_util.GetUpdateLabelsDictFromArgs(args)
    vdrpo = hooks.ReadVolumeDataRestorePolicyOverridesFile(
        args.volume_data_restore_policy_overrides_file
    )
    restore_ref = args.CONCEPTS.restore.Parse()
    restore_filter = hooks.ReadRestoreFilterFile(args.filter_file)
    if args.IsSpecified('async'):
      return api_util.CreateRestore(
          restore_ref,
          backup=args.backup,
          description=args.description,
          labels=labels,
          volume_data_restore_policy_overrides=vdrpo,
          restore_filter=restore_filter,
      )
    api_util.CreateRestoreAndWaitForLRO(
        restore_ref=restore_ref,
        backup=args.backup,
        description=args.description,
        labels=labels,
        volume_data_restore_policy_overrides=vdrpo,
        restore_filter=restore_filter,
    )
    if not args.IsSpecified('wait_for_completion'):
      return []
    return api_util.WaitForRestoreToFinish(restore_ref.RelativeName())
