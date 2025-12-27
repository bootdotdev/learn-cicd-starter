# -*- coding: utf-8 -*- #
# Copyright 2020 Google LLC. All Rights Reserved.
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
"""List Artifact Registry and Container Registry repositories."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.artifacts import flags
from googlecloudsdk.command_lib.artifacts import util

DEFAULT_LIST_FORMAT = """\
    table[title="ARTIFACT_REGISTRY"](
         name.basename():label=REPOSITORY,
         format:label=FORMAT,
         mode.basename(undefined=STANDARD_REPOSITORY):label=MODE,
         description:label=DESCRIPTION,
         name.segment(3):label=LOCATION,
         labels.list():label=LABELS,
         kmsKeyName.yesno(yes='Customer-managed key', no='Google-managed key'):label=ENCRYPTION,
         createTime.date(tz=LOCAL),
         updateTime.date(tz=LOCAL),
         sizeBytes.size(zero='0',precision=3,units_out=M):label="SIZE (MB)"
    )"""


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class List(base.ListCommand):
  """List repositories in the specified project.

  List all Artifact Registry repositories in the specified project.

  To specify the maximum number of repositories to list, use the --limit flag.
  """

  detailed_help = {
      "DESCRIPTION":
          "{description}",
      "EXAMPLES":
          """\
    The following command lists a maximum of five repositories:

        $ {command} --limit=5

    To list repositories with name as `my_repo`:

        $ {command} --filter='name="projects/my-project/locations/us/repositories/my_repo"'

    To list repositories with a given partial name, use `*` to match any character in name:

        $ {command} --filter='name="projects/my-project/locations/us/repositories/*repo"'

        $ {command} --filter='name="projects/my-project/locations/us/repositories/my_*"'

    To list files that have annotations:

        $ {command} --filter=annotations:*

    To list repositories with annotations pair as [annotation_key: annotation_value]

        $ {command} --filter='annotations.annotation_key:annotation_value'

    To list repositories with annotations containing key as `my_key`:

        $ {command} --filter='annotations.my_key'

    If the key or value contains special characters, such as `my.key` or `my.value`, backtick("`") is required:

        $ {command} --filter='annotations.`my.key`'

        $ {command} --filter='annotations.`my.key`:`my.value`'

    To list repositories with given partial annotation key or value, use `*` to match any character:

        $ {command} --filter='annotations.*key:`*.value`'

    To list repositories ordered by create_time:

        $ {command} --sort-by=create_time

    To list repositories ordered by update_time reversely:

        $ {command}--sort-by=~update_time
    """,
  }

  @staticmethod
  def Args(parser):
    parser.display_info.AddFormat(DEFAULT_LIST_FORMAT)
    base.URI_FLAG.RemoveFromParser(parser)
    flags.GetOptionalLocationFlag().AddToParser(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      A list of Repositories.
    """
    return util.ListRepositories(args)
