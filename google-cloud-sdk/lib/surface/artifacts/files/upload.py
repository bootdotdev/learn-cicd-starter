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
"""Upload files to Artifact Registry."""

import os

from apitools.base.py import transfer
from googlecloudsdk.api_lib.artifacts import exceptions as ar_exceptions
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.artifacts import flags
from googlecloudsdk.command_lib.artifacts import util
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources
from googlecloudsdk.core.util import scaled_integer


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.Hidden
class Upload(base.Command):
  """Uploads files to Artifact Registry."""

  api_version = 'v1'

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
    To upload a file located in /path/to/file/ to a repository in "us-central1":

        $ {command} --location=us-central1 --project=myproject --repository=myrepo \
          --file=myfile --source=/path/to/file/

    To upload all files located in directory /path/to/file/ to a repository in "us-central1":

        $ {command} --location=us-central1 --project=myproject --repository=myrepo \
          --source-directory=/path/to/file/
    """,
  }

  @staticmethod
  def Args(parser):
    """Set up arguments for this command.

    Args:
      parser: An argparse.ArgumentPaser.
    """
    flags.GetRequiredRepoFlag().AddToParser(parser)
    flags.GetSkipExistingFlag().AddToParser(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    group = parser.add_group(mutex=True, required=True)

    parser.add_argument(
        '--file',
        metavar='FILE',
        required=False,
        help=(
            'The name under which the file will be uploaded. '
            'If not specified, the name of the local file is used.'
        ),
    )
    group.add_argument(
        '--source',
        metavar='SOURCE',
        help='The path to the file you are uploading.',
    )
    group.add_argument(
        '--source-directory',
        metavar='SOURCE_DIRECTORY',
        help='The directory you are uploading.',
    )

  def Run(self, args):
    """Run the file upload command."""

    client = apis.GetClientInstance('artifactregistry', self.api_version)
    messages = client.MESSAGES_MODULE

    source_dir = args.source_directory
    source_file = args.source

    if source_file and args.skip_existing:
      raise ar_exceptions.InvalidInputValueError(
          'Skip existing is not supported for single file uploads.'
      )

    if source_dir and args.async_:
      raise ar_exceptions.InvalidInputValueError(
          'Asynchronous uploads not supported for directories.'
      )

    if source_dir and args.file:
      raise ar_exceptions.InvalidInputValueError(
          'File name is not supported for directory uploads.'
      )

    # Uploading a single file
    if source_file:
      return self.uploadArtifact(args, source_file, client, messages)
    # Uploading a directory
    elif source_dir:
      # If source_dir was specified, expand, normalize and traverse
      # through the directory sending one upload request per file found.
      args.source_directory = os.path.normpath(os.path.expanduser(source_dir))
      if not os.path.isdir(args.source_directory):
        raise ar_exceptions.InvalidInputValueError(
            'Specified path is not an existing directory.'
        )
      log.status.Print('Uploading directory: {}'.format(source_dir))
      for path, _, files in os.walk(args.source_directory):
        for file in files:
          try:
            self.uploadArtifact(
                args, (os.path.join(path, file)), client, messages
            )
          except waiter.OperationError as e:
            if args.skip_existing and 'already exists' in str(e):
              log.warning('File with the same ID already exists.')
              continue
            raise

  def uploadArtifact(self, args, file_path, client, messages):
    # Default chunk size to be consistent for uploading to clouds.
    chunksize = scaled_integer.ParseInteger(
        properties.VALUES.storage.upload_chunk_size.Get()
    )
    repo_ref = args.CONCEPTS.repository.Parse()
    # If file name was not specified in the arguments, take the last portion
    # of the file path as the file name.
    # ie. file path is folder1/folder2/file.txt, the file name is file.txt
    file_name = os.path.basename(file_path)
    if args.file:
      file_name = args.file

    request = messages.ArtifactregistryProjectsLocationsRepositoriesFilesUploadRequest(
        uploadFileRequest=messages.UploadFileRequest(fileId=file_name),
        parent=repo_ref.RelativeName(),
    )

    mime_type = util.GetMimetype(file_path)
    upload = transfer.Upload.FromFile(
        file_path, mime_type=mime_type, chunksize=chunksize
    )
    op_obj = client.projects_locations_repositories_files.Upload(
        request, upload=upload
    )
    op = op_obj.operation
    op_ref = resources.REGISTRY.ParseRelativeName(
        op.name, collection='artifactregistry.projects.locations.operations'
    )

    # Handle the operation.
    if args.async_:
      return op_ref
    else:
      result = waiter.WaitFor(
          waiter.CloudOperationPollerNoResources(
              client.projects_locations_operations
          ),
          op_ref,
          'Uploading file: {}'.format(file_name),
      )
      return result
