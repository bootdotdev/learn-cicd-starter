# -*- coding: utf-8 -*- #
# Copyright 2013 Google LLC. All Rights Reserved.
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

"""The command to restore a backup of a Google Cloud CLI installation."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.components import util


@base.Hidden
@base.Deprecate(
    is_removed=False,
    warning=(
        'Starting with release 473.0.0, the Google Cloud CLI updates in place'
        ' instead of making a backup copy of the installation directory when'
        ' running `gcloud components update`, `install`, and `remove` commands'
        ' (this reduces the time taken by those operations). Consequently, this'
        ' command has no backup to restore in those cases. Instead, to restore'
        ' your installation to a previous version, run'
        ' `gcloud components update --version=<previous_version>`, or install'
        ' the previous version directly from'
        ' https://cloud.google.com/sdk/docs/install.'
    ),
)
@base.UniverseCompatible
class Restore(base.SilentCommand):
  """Restore the Google Cloud CLI installation to its state before a reinstall.

  This is an undo operation, which restores the Google Cloud CLI installation on
  the local workstation to the state it was in just before the most recent
  `{parent_command} reinstall` command. A `restore` command does not undo a
  previous `restore` command.

  ## EXAMPLES
  To restore the Google Cloud CLI installation to its state before reinstalling,
  run:

    $ {command}
  """

  @staticmethod
  def Args(_):
    pass

  def Run(self, args):
    """Runs the restore command."""
    update_manager = util.GetUpdateManager(args)
    update_manager.Restore()
