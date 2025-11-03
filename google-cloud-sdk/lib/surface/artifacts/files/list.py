# -*- coding: utf-8 -*- #
# Copyright 2022 Google LLC. All Rights Reserved.
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
"""List Artifact Registry files."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.artifacts import file_util
from googlecloudsdk.command_lib.artifacts import flags

DEFAULT_LIST_FORMAT = """\
    table(
      name.basename().sub("%2F", "/").sub("%2B", "+").sub("%5E", "^"):label=FILE,
      createTime.date(tz=LOCAL),
      updateTime.date(tz=LOCAL),
      sizeBytes.size(zero='0',precision=3,units_out=M):label="SIZE (MB)",
      owner:label=OWNER,
      annotations
    )"""


@base.DefaultUniverseOnly
class List(base.ListCommand):
  """List Artifact Registry files.

  List all Artifact Registry files in the specified repository and location.

  To specify the maximum number of files to list, use the --limit flag.
  """

  detailed_help = {
      'DESCRIPTION':
          '{description}',
      'EXAMPLES':
          """\
      To list files in the current project under repository `my-repo` in `us`:

          $ {command} --repository=my-repo --location=us

      The following command lists a maximum of five files:

          $ {command} --repository=my-repo --location=us --limit=5

      To list files in the current project under repository `my-repo` in `us` owned by package `my-package`:

          $ {command} --repository=my-repo --location=us --package=my-package

      To list files in the current project under repository `my-repo` in `us` owned by package `my-package` and version `1.0.0`:

          $ {command} --repository=my-repo --location=us --package=my-package --version=1.0.0

      To list files in the current project under repository `my-repo` in `us` owned by package `my-package` and tag name `my-tag`:

          $ {command} --repository=my-repo --location=us --package=my-package --tag=my-tag

      To list files with name as `my-file`:

          $ {command} --filter='name="projects/my-project/locations/us/repositories/my-repo/files/my-file"'

      To list files with a given partial name, use `*` to match any character in name:

          $ {command} --filter='name="projects/my-project/locations/us/repositories/my-repo/files/*file"'

          $ {command} --filter='name="projects/my-project/locations/us/repositories/my-repo/files/my-*"'

      To list files that have annotations:

          $ {command} --filter=annotations:*

      To list files with annotations pair as [annotation_key: annotation_value]

          $ {command} --filter='annotations.annotation_key:annotation_value'

      To list files with annotations containing key as `my_key`:

          $ {command} --filter='annotations.my_key'

          If the key or value contains special characters, such as `my.key` and `my.value`, backtick("`") is required:

          $ {command} --filter='annotations.`my.key`'

          $ {command} --filter='annotations.`my.key`:`my.value`'

      To list files with given partial annotation key or value, use `*` to match any character:

          $ {command} --filter='annotations.*key:`*.value`'

      To list files in the current project under repository `my-repo` in `us`, ordering by create_time:

          $ {command} --repository=my-repo --location=us --sort-by=create_time

      To list files in the current project under repository `my-repo` in `us`, ordering by update_time reversely:

          $ {command} --repository=my-repo --location=us --sort-by=~update_time

      """,
  }

  @staticmethod
  def Args(parser):
    parser.display_info.AddFormat(DEFAULT_LIST_FORMAT)
    base.URI_FLAG.RemoveFromParser(parser)
    flags.GetRepoFlag().AddToParser(parser)
    parser.add_argument(
        '--package',
        required=False,
        help='List all files in a specified artifact, such as a container image or a language package. If you do not use --tag or --version in the command, the command lists files in all versions of the artifact.'
    )
    parser.add_argument(
        '--version',
        required=False,
        help='List all files in the specified artifact version. Use the --package flag to specify the artifact.'
    )
    parser.add_argument(
        '--tag',
        required=False,
        help='List all files in the artifact version with the specified tag. This flag only works with formats that use tags, such as container images. Use the --package flag to specify the artifact.'
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      A list of files.
    """

    return file_util.ListFiles(args)
