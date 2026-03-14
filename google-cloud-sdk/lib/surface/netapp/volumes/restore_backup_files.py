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
"""Restores selected files from a backup to a specified Volume."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.netapp.volumes import client as volumes_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp import flags
from googlecloudsdk.command_lib.netapp.volumes import flags as volumes_flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class RestoreBackupFiles(base.Command):
  """Restore specific files from a backup to a Volume."""

  _RELEASE_TRACK = base.ReleaseTrack.ALPHA

  detailed_help = {
      'DESCRIPTION': """\
          Restore specific files from a backup to a Volume
          """,
      'EXAMPLES': """\
          The following command restores file1.txt and file2.txt from the given backup to a Volume named NAME to the directory /path/to/destination/directory.

              $ {command} NAME --location=us-central1 --backup=backup-1 --file-list=file1.txt,file2.txt --restore-destination-path=/path/to/destination/directory
          """,
  }

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser(
        [flags.GetVolumePresentationSpec('The Volume to restore into.')]
    ).AddToParser(parser)
    volumes_flags.AddVolumeRestoreFromBackupArg(parser)
    volumes_flags.AddVolumeRestoreDestinationPathArg(parser)
    volumes_flags.AddVolumeRestoreFileListArg(parser)
    flags.AddResourceAsyncFlag(parser)

  def Run(self, args):
    """Run the restore command."""
    volume_ref = args.CONCEPTS.volume.Parse()
    client = volumes_client.VolumesClient(release_track=self._RELEASE_TRACK)
    revert_warning = (
        'You are about to restore files from a backup to Volume {}.\n'
        'Are you sure?'.format(volume_ref.RelativeName())
    )
    if not console_io.PromptContinue(message=revert_warning):
      return None
    result = client.RestoreVolume(
        volume_ref,
        args.backup,
        args.file_list,
        args.restore_destination_path,
        args.async_,
    )
    if args.async_:
      command = 'gcloud {} netapp volumes list'.format(
          self.ReleaseTrack().prefix
      )
      log.status.Print(
          'Check the status of the volume being restored by listing all'
          ' volumes:\n$ {}'.format(command)
      )
    return result


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class RestoreBackupFilesBeta(RestoreBackupFiles):
  """Restore specific files from a backup to a Volume."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA


@base.ReleaseTracks(base.ReleaseTrack.GA)
class RestoreBackupFilesGA(RestoreBackupFiles):
  """Restore specific files from a backup to a Volume."""

  _RELEASE_TRACK = base.ReleaseTrack.GA
