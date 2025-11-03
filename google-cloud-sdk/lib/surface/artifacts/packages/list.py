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
"""List Artifact Registry packages."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.artifacts import flags
from googlecloudsdk.command_lib.artifacts import package_util

DEFAULT_LIST_FORMAT = """\
    table(
         name.sub("%5E", "^"):label=PACKAGE,
         createTime.date(tz=LOCAL),
         updateTime.date(tz=LOCAL),
         annotations
       )"""


@base.DefaultUniverseOnly
class List(base.ListCommand):
  """List Artifact Registry packages.

  List all Artifact Registry packages in the specified repository and project.

  To specify the maximum number of packages to list, use the --limit flag.
  """
  detailed_help = {
      'DESCRIPTION':
          '{description}',
      'EXAMPLES':
          """\

      The following command lists a maximum of five packages:

          $ {command} --limit=5

      To list packages with name as `my-pkg`:

          $ {command} --filter='name="projects/my-project/locations/us/repositories/my-repo/packages/my-pkg"

      To list packages with a given partial name, use `*` to match any character in name:

          $ {command} --filter='name="projects/my-project/locations/us/repositories/my-repo/packages/*pkg"'

          $ {command} --filter='name="projects/my-project/locations/us/repositories/my-repo/packages/my*"'

      To list files that have annotations:

          $ {command} --filter=annotations:*

      To list packages with annotations pair as [annotation_key: annotation_value]:

          $ {command} --filter='annotations.annotation_key:annotation_value'

      To list packages with annotations containing key as `my_key`:

          $ {command} --filter='annotations.my_key'

          If the key or value contains special characters, such as `my.key` or `my.value`, backtick("`") is required:

          $ {command} --filter='annotations.`my.key`'

          $ {command} --filter='annotations.`my.key`:`my.value`'

      To list packages with given partial annotation key or value, use `*` to match any character:

          $ {command} --filter='annotations.my_*:`*.value`'

      To list packages ordered by create_time:

        $ {command} --sort-by=create_time

      To list packages ordered by update_time reversely:

        $ {command} --sort-by=~update_time
  """
  }

  @staticmethod
  def Args(parser):
    parser.display_info.AddFormat(DEFAULT_LIST_FORMAT)
    base.URI_FLAG.RemoveFromParser(parser)
    flags.GetRepoFlag().AddToParser(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      A list of packages.
    """
    return package_util.ListPackages(args)
