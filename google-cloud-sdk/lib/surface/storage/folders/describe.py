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

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.storage import api_factory
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import errors_util
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.command_lib.storage import storage_url
from googlecloudsdk.command_lib.storage.resources import full_resource_formatter
from googlecloudsdk.command_lib.storage.resources import resource_util


@base.DefaultUniverseOnly
class Describe(base.DescribeCommand):
  """Describe hierarchical namesapace bucket folders."""

  detailed_help = {
      'DESCRIPTION': """Describe hierarchical namespace bucket folders.""",
      'EXAMPLES': """
      The following command shows information about a folder named
      `folder` in an hierarchical namespace bucket called `my-bucket`:

        $ {command} gs://my-bucket/folder/
      """,
  }

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'url',
        type=str,
        help='The URL of the folder to describe.',
    )
    flags.add_additional_headers_flag(parser)
    flags.add_raw_display_flag(parser)

  def Run(self, args):
    url = storage_url.storage_url_from_string(args.url)
    errors_util.raise_error_if_not_gcs_folder_type(
        args.command_path, url, 'folder'
    )
    client = api_factory.get_api(url.scheme)
    resource = client.get_folder(
        url.bucket_name,
        url.resource_name,
    )
    return resource_util.get_display_dict_for_resource(
        resource,
        full_resource_formatter.FolderDisplayTitlesAndDefaults,
        display_raw_keys=args.raw,
    )
