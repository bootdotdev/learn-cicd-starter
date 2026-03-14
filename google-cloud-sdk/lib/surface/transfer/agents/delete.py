# -*- coding: utf-8 -*- #
# Copyright 2021 Google LLC. All Rights Reserved.
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
"""Command to delete transfer agents."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.transfer import agents_util
from googlecloudsdk.core.resource import resource_printer


_DELETE_SPECIFIC_AGENTS_MESSAGE = """\
To delete specific agents on your machine, run the following command:

{container_manager} stop {container_ids}

Note: If you encounter a permission error or cannot find the agent, you may need
to add "sudo" before "{container_manager}".
"""
_DELETE_ALL_AGENTS_MESSAGE = """\
To delete all agents on your machine, run the following command:

{container_manager} stop $({container_manager} container list --quiet --all --filter ancestor=gcr.io/cloud-ingest/tsop-agent)

Note: If you encounter a permission error, you may need to add "sudo" before both instances of "{container_manager}".
"""
_UNINSTALL_MESSAGE = """\
To delete all agents on your machine and uninstall the machine's agent container image, run the following commands:

{container_manager} stop $({container_manager} container list --quiet --all --filter ancestor=gcr.io/cloud-ingest/tsop-agent)

# May take a moment for containers to shutdown before you can run:
{container_manager} image rm gcr.io/cloud-ingest/tsop-agent

Note: If you encounter a permission error, you may need to add "sudo" before all three instances of "{container_manager}".
"""
_LIST_AGENTS_MESSAGE = """\
Pick which agents to delete. You can include --all to delete all agents on your machine or --ids to specify agent IDs. You can find agent IDs by running:

{container_manager} container list --all --filter ancestor=gcr.io/cloud-ingest/tsop-agent
"""


_DELETE_COMMAND_DESCRIPTION_TEXT = """\
Delete Transfer Service agents from your machine.
"""

_DELETE_COMMAND_EXAMPLES_TEXT = """\
If you plan to delete specific agents, you can list which agents are running on your machine by running:

  $ {container_managers} container list --all --filter ancestor=gcr.io/cloud-ingest/tsop-agent

Then run:

  $ {{command}} --ids=id1,id2,...
"""


def _get_detailed_help_text(release_track):
  """Returns the detailed help text for the delete command.

  Args:
    release_track (base.ReleaseTrack): The release track.

  Returns:
    A dict containing keys DESCRIPTION, EXAMPLES that provides detailed help.
  """
  is_alpha = release_track == base.ReleaseTrack.ALPHA
  container_managers = 'docker (or podman)' if is_alpha else 'docker'
  return {
      'DESCRIPTION': _DELETE_COMMAND_DESCRIPTION_TEXT,
      'EXAMPLES': _DELETE_COMMAND_EXAMPLES_TEXT.format(
          container_managers=container_managers
      ),
  }


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Delete(base.Command):
  """Delete Transfer Service transfer agents."""

  detailed_help = _get_detailed_help_text(base.ReleaseTrack.GA)

  @staticmethod
  def Args(parser):
    mutually_exclusive_flags_group = parser.add_group(
        mutex=True, sort_args=False
    )
    mutually_exclusive_flags_group.add_argument(
        '--ids',
        type=arg_parsers.ArgList(),
        metavar='IDS',
        help=(
            'The IDs of the agents you want to delete. Separate multiple agent'
            ' IDs with commas, with no spaces following the commas.'
        ),
    )
    mutually_exclusive_flags_group.add_argument(
        '--all',
        action='store_true',
        help='Delete all agents running on your machine.',
    )
    mutually_exclusive_flags_group.add_argument(
        '--uninstall',
        action='store_true',
        help=(
            'Fully uninstall the agent container image in addition to deleting'
            ' the agents. Uninstalling the container image will free up space,'
            " but you'll need to reinstall it to run agents on this machine in"
            ' the future.'
        ),
    )

  def Display(self, args, resources):
    del args  # Unused.
    resource_printer.Print(resources, 'object')

  def Run(self, args):
    container_manager = agents_util.ContainerManager.from_args(args)

    if args.ids:
      return _DELETE_SPECIFIC_AGENTS_MESSAGE.format(
          container_manager=container_manager.value,
          container_ids=' '.join(args.ids),
      )
    if args.all:
      return _DELETE_ALL_AGENTS_MESSAGE.format(
          container_manager=container_manager.value,
      )
    if args.uninstall:
      return _UNINSTALL_MESSAGE.format(
          container_manager=container_manager.value,
      )
    return _LIST_AGENTS_MESSAGE.format(
        container_manager=container_manager.value,
    )


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class DeleteAlpha(Delete):
  """Delete Transfer Service transfer agents."""

  detailed_help = _get_detailed_help_text(base.ReleaseTrack.ALPHA)

  @staticmethod
  def Args(parser):
    Delete.Args(parser)
    # TODO(b/377355485) - Once Podman support is GA, move this flag to GA track.
    parser.add_argument(
        '--container-manager',
        choices=sorted(
            [option.value for option in agents_util.ContainerManager]
        ),
        default=agents_util.ContainerManager.DOCKER.value,
        help='The container manager to use for running agents.',
    )
