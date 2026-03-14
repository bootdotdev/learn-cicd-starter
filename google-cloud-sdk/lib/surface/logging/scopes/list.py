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

"""'logging scopes list' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.logging import util
from googlecloudsdk.calliope import base

DETAILED_HELP = {
    'DESCRIPTION': """
        List the log scopes for a project.
    """,
    'EXAMPLES': """
     To list the log scopes in a project, run:

        $ {command} --project=my-project
    """,
}


@base.UniverseCompatible
class List(base.ListCommand):
  """List the defined log scopes."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    util.AddParentArgs(
        parser, 'log scopes to list', exclude_billing_account=True
    )

    parser.display_info.AddFormat(
        'table(name.segment(-3):label=LOCATION, '
        'name.segment(-1):label=LOG_SCOPE_ID, '
        'resource_name, description, create_time, update_time)'
    )
    parser.display_info.AddCacheUpdater(None)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Yields:
      The list of log scopes.
    """
    result = util.GetClient().projects_locations_logScopes.List(
        util.GetMessages().LoggingProjectsLocationsLogScopesListRequest(
            parent=util.CreateResourceName(
                util.GetProjectResource(args.project).RelativeName(),
                'locations',
                'global',
            ),
        )
    )
    for scope in result.logScopes:
      yield scope


List.detailed_help = DETAILED_HELP
