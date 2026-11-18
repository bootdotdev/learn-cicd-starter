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
"""List Artifact Registry tags."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.artifacts import flags
from googlecloudsdk.command_lib.artifacts import tag_util

DEFAULT_LIST_FORMAT = """\
    table(
         name.basename():label=TAG,
         version.basename():label=VERSION
      )"""


@base.UniverseCompatible
class List(base.ListCommand):
  """List Artifact Registry tags.

  List all Artifact Registry tags in the specified package.

  This command can fail for the following reasons:
    * The specified version or package does not exist.
    * The active account does not have permission to list tags.
    * The specified package format doesn't support tag operations (e.g. maven).

  To specify the maximum number of tags to list, use the --limit flag.
  """
  detailed_help = {
      'DESCRIPTION':
          '{description}',
      'EXAMPLES':
          """\

      To list tags for package `my-package`:

         $ {command} --package=my-package

      The following command lists a maximum of five tags for package `my-package`:

         $ {command} --package=my-package --limit=5

      To list tags of package `my-package` with name as `my-tag`:

          $ {command} --package=my-package --filter='name="projects/my-project/locations/us/repositories/my-repo/packages/my-package/tags/my-tag"'

      To list tags of package `my-package` with a given partial name, use `*` to match any character in name:

          $ {command} --package=my-package --filter='name="projects/my-project/locations/us/repositories/my-repo/packages/my-package/tags/my*"'

          $ {command} --package=my-package --filter='name="projects/my-project/locations/us/repositories/my-repo/packages/my-package/tags/*tag"'
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
        help="""List all tags in a specified artifact, such as a container
        image or a language package."""
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      A list of package tags.
    """
    return tag_util.ListTags(args)
