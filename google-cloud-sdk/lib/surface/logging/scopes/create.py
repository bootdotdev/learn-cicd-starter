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
"""'logging scopes create' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.logging import util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Create(base.CreateCommand):
  """Create a log scope.

  After creating a log scope, you can use it to view logs in 1 or more
  resources.

  ## EXAMPLES

  To create a log scope in a project, run:

    $ {command} my-scope --resource-names=projects/my-project

  To create a log scope in a project with a description, run:

    $ {command} my-scope --resource-names=projects/my-project --description="my
    custom log scope"

  To create a log scope that contains more than 1 resource, such as projects and
  views, run:

    $ {command} my-scope
    --resource-names=projects/my-project,projects/my-project2,
    projects/my-project/locations/global/buckets/my-bucket/views/my-view1,
    projects/my-project/locations/global/buckets/my-bucket/views/my-view2,
  """

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument('LOG_SCOPE_ID', help='ID of the log scope to create.')
    parser.add_argument(
        '--description', help='A textual description for the log scope.'
    )
    parser.add_argument(
        '--resource-names',
        help=(
            ' Comma-separated list of resource names in this log scope. It'
            ' could be one or more parent resources or one or more views. '
            ' A log scope can include a maximum of 50 projects and a maximum of'
            ' 100 resources in total. For example, projects/[PROJECT_ID],'
            ' projects/[PROJECT_ID]/locations/[LOCATION_ID]/buckets/[BUCKET_ID]/views/[VIEW_ID]`'
        ),
        metavar='RESOURCE_NAMES',
        required=True,
        type=arg_parsers.ArgList(),
    )
    util.AddParentArgs(
        parser, 'log scope to create', exclude_billing_account=True
    )

  def _Run(self, args):
    scope_data = {}
    if args.IsSpecified('description'):
      scope_data['description'] = args.description
    if args.IsSpecified('resource_names'):
      scope_data['resourceNames'] = args.resource_names

      return util.GetClient().projects_locations_logScopes.Create(
          util.GetMessages().LoggingProjectsLocationsLogScopesCreateRequest(
              logScope=util.GetMessages().LogScope(**scope_data),
              logScopeId=args.LOG_SCOPE_ID,
              parent=util.CreateResourceName(
                  util.GetProjectResource(args.project).RelativeName(),
                  'locations',
                  'global',
              ),
          )
      )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      The created log scope.
    """
    return self._Run(args)
