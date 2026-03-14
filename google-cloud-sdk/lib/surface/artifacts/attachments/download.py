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
"""Implements the command to download attachments from a repository."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import os

from googlecloudsdk.api_lib.artifacts import exceptions as ar_exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.artifacts import attachment_util
from googlecloudsdk.command_lib.artifacts import download_util
from googlecloudsdk.command_lib.artifacts import flags
from googlecloudsdk.command_lib.artifacts import requests
from googlecloudsdk.core import log
from six.moves.urllib.parse import unquote


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Download(base.Command):
  """Download an Artifact Registry attachment from a repository."""

  api_version = 'v1'

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
    To download the attachment `my-attachment` to `/path/to/destination/`:

        $ {command} my-attachment --destination=/path/to/destination/

    To download the attachment `my-attachment` in 8000 byte chunks to `/path/to/destination/`:

        $ {command} my-attachment --destination=/path/to/destination/ \
            --chunk-size=8000

    To download the attachment `my-attachment` using parallel multipart download with 4 threads:

        $ {command} my-attachment --destination=/path/to/destination/ \
            --parallelism=4

    For Docker-format repositories only: to download the attachment stored in the OCI version `projects/my-project/locations/us/repositories/my-repo/packages/my-package/versions/sha256:123` to `/path/to/destination/`:

        $ {command} --oci-version-name=projects/my-project/locations/us/repositories/my-repo/packages/my-package/versions/sha256:123 --destination=/path/to/destination/

    For Docker-format repositories only: to download the attachment stored in the OCI version with URI `us-docker.pkg.dev/my-project/my-repo/my-package@sha256:123` to `/path/to/destination/`:

        $ {command} --oci-version-name=us-docker.pkg.dev/my-project/my-repo/my-package@sha256:123 --destination=/path/to/destination/
    """,
  }

  @staticmethod
  def Args(parser):
    """Set up arguments for this command.

    Args:
      parser: An argparse.ArgumentParser.
    """
    flags.GetOptionalAttachmentFlag().AddToParser(parser)
    flags.GetChunkSize().AddToParser(parser)
    parser.add_argument(
        '--oci-version-name',
        metavar='OCI_VERSION_NAME',
        required=False,
        help=(
            'For Docker-format repositories only. The version name of the OCI'
            ' artifact to download.'
        ),
    )
    parser.add_argument(
        '--destination',
        metavar='DESTINATION',
        required=True,
        help='Path where you want to save the downloaded attachment files.',
    )
    parser.add_argument(
        '--parallelism',
        metavar='PARALLELISM',
        help=(
            'Specifies the number of threads to use for downloading the'
            ' attachment files in parallel.'
        ),
    )

  def Run(self, args):
    """Runs the attachment download command."""

    args.destination = os.path.expanduser(args.destination)
    if not os.path.exists(args.destination):
      raise ar_exceptions.DirectoryNotExistError(
          'Destination directory does not exist: ' + args.destination
      )
    if not os.path.isdir(args.destination):
      raise ar_exceptions.PathNotDirectoryError(
          'Destination is not a directory: ' + args.destination
      )
    # Get the attachment.
    attachment = attachment_util.GetAttachmentToDownload(args)
    self.download_files(args, attachment.files)

  def download_files(self, args, files):
    default_chunk_size = 3 * 1024 * 1024
    chunk_size = args.chunk_size or default_chunk_size
    parallelism = args.parallelism or 1
    for file in files:
      # Extract just the file id.
      # ...files/sha256:123 -> 123
      # ...files/sha256:pkg%2Fv1.0 -> pkg/v1.0
      file_id = os.path.basename(file)
      try:
        default_file_name = unquote(file_id.rsplit(':', 1)[1])
      except IndexError:
        default_file_name = file_id
      file_name = self.get_file_name(file, default_file_name)
      final_path = os.path.join(args.destination, file_name)
      download_util.Download(
          final_path,
          file,
          file_name,
          False,
          int(chunk_size),
          parallelism=int(parallelism),
      )
      log.status.Print(
          'Successfully downloaded the file to {}'.format(args.destination)
      )

  def get_file_name(self, file, default_file_name):
    client = requests.GetClient()
    messages = requests.GetMessages()
    request = (
        messages.ArtifactregistryProjectsLocationsRepositoriesFilesGetRequest(
            name=file
        )
    )
    resp = client.projects_locations_repositories_files.Get(request)
    if resp.annotations is not None:
      for e in resp.annotations.additionalProperties:
        if e.key == 'artifactregistry.googleapis.com/file_name':
          return e.value

    return default_file_name
