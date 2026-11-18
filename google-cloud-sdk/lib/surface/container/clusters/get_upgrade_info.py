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
"""Get cluster upgrade info command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base


@base.UniverseCompatible
class GetUpgradeInfo(base.Command):
  """Get information about upgrades for existing clusters including auto upgrade status, upgrade history, upgrade targets, and end of support timelines."""

  detailed_help = {
      'DESCRIPTION':
          '{description}',
      'EXAMPLES':
          """\
          To get upgrade information for an existing cluster, run:

            $ {command} sample-cluster
          """,
  }

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: An argparse.ArgumentParser-like object. It is mocked out in order
        to capture some information, but behaves like an ArgumentParser.
    """
    parser.add_argument('name', help='The name of your existing cluster.')

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    adapter = self.context['api_adapter']
    location_get = self.context['location_get']
    location = location_get(args)

    return adapter.GetClusterUpgradeInfo(adapter.ParseCluster(args.name,
                                                              location))
