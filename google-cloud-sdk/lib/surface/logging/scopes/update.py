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
"""'logging scopes update' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.logging import util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as calliope_exceptions

DETAILED_HELP = {
    'DESCRIPTION': """
        Update the properties of a log scope.
    """,
    'EXAMPLES': """
     To update the description of a log scope in a project, run:

        $ {command} my-scope --description=my-new-description --project=my-project

     To update the resource name of a log scope in a project. Ensure that you
     provide all the resource names including the existing ones. For example,
     if the log scope has the resource name my-project, and you want to update
     the log scope to have the resource name another-project, run the following:

        $ {command} my-scope --resource-names=projects/my-project,projects/another-project --project=my-project
    """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Update(base.UpdateCommand):
  """Update a log scope.

  Changes one or more properties associated with a log scope.
  """

  def __init__(self, *args, **kwargs):
    super(Update, self).__init__(*args, **kwargs)
    self._current_scope = None

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument(
        'LOG_SCOPE_ID', help='The ID of the log scope to update.'
    )
    parser.add_argument(
        '--description', help='A new description for the log scope.'
    )
    parser.add_argument(
        '--resource-names',
        help='A new set of resource names for the log scope.',
        type=arg_parsers.ArgList(),
        metavar='RESOURCE_NAMES',
    )

  def _Run(self, args):
    scope_data = {}
    update_mask = []
    parameter_names = ['--description', '--resource-names']
    if args.IsSpecified('description'):
      scope_data['description'] = args.description
      update_mask.append('description')
    if args.IsSpecified('resource_names'):
      scope_data['resourceNames'] = args.resource_names
      update_mask.append('resource_names')

    if not update_mask:
      raise calliope_exceptions.MinimumArgumentException(
          parameter_names, 'Please specify at least one property to update'
      )

    return util.GetClient().projects_locations_logScopes.Patch(
        util.GetMessages().LoggingProjectsLocationsLogScopesPatchRequest(
            name=util.CreateResourceName(
                util.CreateResourceName(
                    util.GetProjectResource(args.project).RelativeName(),
                    'locations',
                    'global',
                ),
                'logScopes',
                args.LOG_SCOPE_ID,
            ),
            logScope=util.GetMessages().LogScope(**scope_data),
            updateMask=','.join(update_mask),
        )
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      The updated log scope.
    """
    return self._Run(args)


Update.detailed_help = DETAILED_HELP
