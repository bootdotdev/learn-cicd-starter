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

"""'logging scopes describe' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.logging import util
from googlecloudsdk.calliope import base

DETAILED_HELP = {
    'DESCRIPTION': """
        Display information about a log scope.
    """,
    'EXAMPLES': """
     To describe a log scope in a project, run:

        $ {command} my-scope --project=my-project
    """,
}


@base.UniverseCompatible
class Describe(base.DescribeCommand):
  """Display information about a log scope."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument(
        'LOG_SCOPE_ID', help='The ID of the log scope to describe.'
    )
    util.AddParentArgs(
        parser, 'log scope to describe', exclude_billing_account=True
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      The specified log scope.
    """
    return util.GetClient().projects_locations_logScopes.Get(
        util.GetMessages().LoggingProjectsLocationsLogScopesGetRequest(
            name=util.CreateResourceName(
                util.CreateResourceName(
                    util.GetParentFromArgs(args, exclude_billing_account=True),
                    'locations',
                    'global',
                ),
                'logScopes',
                args.LOG_SCOPE_ID,
            )
        )
    )


Describe.detailed_help = DETAILED_HELP
