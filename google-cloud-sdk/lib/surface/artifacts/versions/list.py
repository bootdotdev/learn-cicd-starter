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
"""List Artifact Registry versions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.artifacts import flags
from googlecloudsdk.command_lib.artifacts import version_util

DEFAULT_LIST_FORMAT = """\
    table(
         name.basename().sub("%5E", "^"):label=VERSION,
         description,
         createTime.date(tz=LOCAL),
         updateTime.date(tz=LOCAL),
         metadata.imageSizeBytes:label=SIZE,
         annotations
       )"""


@base.DefaultUniverseOnly
class List(base.ListCommand):
  """List Artifact Registry package versions.

  List all Artifact Registry versions in the specified package.

  To specify the maximum number of versions to list, use the --limit flag.
  """
  detailed_help = {
      'DESCRIPTION':
          '{description}',
      'EXAMPLES':
          """\

      The following command lists a maximum of five packages versions:

          $ {command} --limit=5

      To list versions of package `my_pkg` with name as `1.0-SNAPSHOT`:

          $ {command} --package=my_pkg --filter='name="projects/my-project/locations/us/repositories/my-repo/packages/my_pkg/versions/1.0-SNAPSHOT"'

      To list versions of package `my_pkg` with a given partial name, use `*` to match any character in name:

          $ {command} --package=my_pkg --filter='name="projects/my-project/locations/us/repositories/my-repo/packages/my_pkg/versions/1.0*"'

          $ {command} --package=my_pkg --filter='name="projects/my-project/locations/us/repositories/my-repo/packages/my_pkg/versions/*SNAPSHOT"'

      To list versions of package `my_pkg` that have annotations:

          $ {command} --package=my_pkg --filter=annotations:*

      To list versions of package `my_pkg` with annotations pair as [annotation_key: annotation_value]:

          $ {command} --package=my_pkg --filter='annotations.annotation_key:annotation_value'

      To list versions of package `my_pkg` with annotations containing key as `my_key`:

          $ {command} --package=my_pkg --filter=annotations.my_key

          If the key or value contains special characters, such as `my.key` and `my.value`, backtick("`") is required:

          $ {command} --filter='annotations.`my.key`'

          $ {command} --filter='annotations.`my.key`:`my.value`'

      To list versions of package `my_pkg` with given partial annotation key or value, use `*` to match any character:

          $ {command} --filter='annotations.*key:`*.value`'

      To list versions of package `my_pkg` ordered by create_time:

        $ {command} --package=my_pkg --sort-by=create_time

      To list versions of package `my_pkg` ordered by update_time reversely:

        $ {command} --package=my_pkg --sort-by=~update_time
  """
  }

  @staticmethod
  def Args(parser):
    parser.display_info.AddFormat(DEFAULT_LIST_FORMAT)
    base.URI_FLAG.RemoveFromParser(parser)
    flags.GetRepoFlag().AddToParser(parser)
    parser.add_argument(
        '--package',
        required=True,
        help="""List all versions in a specified artifact, such as a container
        image or a language package."""
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      A list of package versions.
    """
    return (
        version_util.ConvertFingerprint(v, args)
        for v in version_util.ListVersions(args)
    )
