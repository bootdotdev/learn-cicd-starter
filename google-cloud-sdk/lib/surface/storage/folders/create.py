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
"""Implementation of create command for making folders in HNS buckets."""


from googlecloudsdk.api_lib.storage import api_factory
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import errors_util
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.command_lib.storage import storage_url
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
class Create(base.Command):
  """Create folders for hierarchical namespace bucket."""

  detailed_help = {
      'DESCRIPTION': 'Create folders.',
      'EXAMPLES': """
      The following command creates a folder called `folder/` in a bucket
      named `my-bucket`:

        $ {command} gs://my-bucket/folder/

      The following command creates all folders in the path `A/B/C/D` in a
      bucket named `my-bucket`:

        $ {command} --recursive gs://my-bucket/folder/A/B/C/D
      """,
  }

  @staticmethod
  def Args(parser):
    """Adds arguments specific to this command to parser."""

    parser.add_argument(
        'url', type=str, nargs='+', help='The URLs of the folders to create.'
    )

    parser.add_argument(
        '--recursive',
        action='store_true',
        help=(
            'Recursively create all folders in a given path if they do not'
            ' alraedy exist.'
        ),
    )

    flags.add_additional_headers_flag(parser)

  def Run(self, args):
    urls = []
    for url_string in args.url:
      url = storage_url.storage_url_from_string(url_string)
      errors_util.raise_error_if_not_gcs_folder_type(
          args.command_path, url, 'folder'
      )
      urls.append(url)

    for url in urls:
      client = api_factory.get_api(url.scheme)
      log.status.Print('Creating {}...'.format(url))
      client.create_folder(url.bucket_name, url.resource_name, args.recursive)
