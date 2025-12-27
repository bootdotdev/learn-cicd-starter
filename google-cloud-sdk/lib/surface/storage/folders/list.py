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
"""Implementation of command for listing folders."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import errors_util
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.command_lib.storage import folder_util
from googlecloudsdk.command_lib.storage import storage_url
from googlecloudsdk.command_lib.storage import wildcard_iterator
from googlecloudsdk.command_lib.storage.resources import full_resource_formatter
from googlecloudsdk.command_lib.storage.resources import resource_util


@base.DefaultUniverseOnly
class List(base.ListCommand):
  """List folders."""

  detailed_help = {
      'DESCRIPTION': """List folders.""",
      'EXAMPLES': """
      The following command lists all folders in a hierarchical namespace bucket:

        $ {command} gs://my-bucket/

      The following command lists all folders under a parent folder:

        $ {command} gs://my-bucket/parent-folder/

      You can use [wildcards](https://cloud.google.com/storage/docs/wildcards)
      to match multiple paths (including multiple buckets). Bucket wildcards are
      expanded to match only buckets contained in your current project. The
      following command matches folders that are stored in buckets
      in your project that begin with ``my-b'':

        $ {command} gs://my-b*/

      Following is another example where we are listing all folders that
      begin with ``B'' under a given bucket:

        $ {command} gs://my-bucket/B*
      """,
  }

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'url', type=str, nargs='+', help='The URLs of the resources to list.'
    )
    flags.add_additional_headers_flag(parser)
    flags.add_raw_display_flag(parser)

  def Run(self, args):
    urls = []
    for url_string in args.url:
      url = storage_url.storage_url_from_string(url_string)
      errors_util.raise_error_if_not_gcs(args.command_path, url)
      urls.append(url)

    for url in urls:
      for resource in wildcard_iterator.CloudWildcardIterator(
          url.join('**'),
          folder_setting=folder_util.FolderSetting.LIST_WITHOUT_OBJECTS,
      ):
        yield resource_util.get_display_dict_for_resource(
            resource,
            full_resource_formatter.FolderDisplayTitlesAndDefaults,
            display_raw_keys=args.raw,
        )
