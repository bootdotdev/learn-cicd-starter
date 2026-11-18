 # -*- coding: utf-8 -*- #
# Copyright 2025 Google LLC. All Rights Reserved.
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
"""Command to list shared templates."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import re
from googlecloudsdk.api_lib.design_center import shared_templates as apis
from googlecloudsdk.api_lib.design_center import utils as api_lib_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import exceptions as core_exceptions
from googlecloudsdk.core import properties

_DETAILED_HELP = {
    'DESCRIPTION': 'List shared templates in a given space.',
    'EXAMPLES': """ \
        To list all shared templates in space `my-space`, project `my-project` and location `us-central1`, run:

          $ {command} --space=my-space --project=my-project --location=us-central1

        Or run:

          $ {command} --space=projects/my-project/locations/us-central1/spaces/my-space

        To list all shared templates from the Google Catalog in location `us-central1`, run:

          $ {command} --google-catalog --location=us-central1

        To filter and list shared templates that contain a `my-shared-template` prefix in the display name in space `my-space`, project `my-project` and location `us-central1`, run:

          $ {command} --space=my-space --project=my-project --location=us-central1 --filter="displayName:my-shared-template*"

        To list up to 10 shared templates in space `my-space`, project `my-project` and location `us-central1`, run:

          $ {command} --space=my-space --project=my-project --location=us-central1 --limit=10
        """,
    'API REFERENCE': """ \
        This command uses the designcenter/v1alpha API. The full documentation for
        this API can be found at:
        http://cloud.google.com/application-design-center/docs
        """,
}

_REQUIRED_FLAGS_BASE_TEXT = (
    'Space resource - The parent space for which shared templates are listed in'
    ' the following format: projects/$project/locations/$location/spaces/$space'
    ' The following arguments in this group can be used to specify the'
    ' attributes of this resource.'
)

_LOCATION_HELP_TEXT = (
    'The location id of the space resource.\n\n'
    'To set the location attribute:\n'
    '  * provide the argument `--space` on the command line'
    ' with a fully specified name;\n'
    '  * provide the argument `--location` on the command line.'
)

_PROJECT_HELP_TEXT = (
    'The project id of the space resource.\n\n'
    'To set the project attribute:\n'
    '  * provide the argument `--space` on the command line'
    ' with a fully specified name;\n'
    '  * provide the argument `--project` on the command line;\n'
    '  * set the property `core/project`.'
)

_SPACE_HELP_TEXT = (
    'ID of the space or fully qualified identifier for the space.\n\n'
    'To set the space attribute:\n'
    '  * provide the argument `--space` on the command line.'
)

_GOOGLE_CATALOG_HELP_TEXT = (
    'If provided, lists all shared template from the Google Catalog.'
    ' This sets the project to "gcpdesigncenter" and space to'
    ' "googlespace".'
)

_BASE_ERROR_MESSAGE = 'Error parsing [space].'

_LOCATION_NOT_SPECIFIED_MESSAGE = (
    'The [space] resource is not properly specified.\n'
    'Failed to find attribute [location]. [location] must be specified unless'
    ' using full resource name for [space]. The attribute can be set in the'
    ' following ways:\n'
    '- provide the argument `--space` on the command line'
    ' with a fully specified name\n'
    '- provide the argument `--location` on the command line'
)

_PROJECT_NOT_SPECIFIED_MESSAGE = (
    'The [space] resource is not properly specified.\n'
    'Failed to find attribute [project]. [project] must be specified unless'
    ' using --google-catalog, a full resource name, or the core/project'
    ' property is set. The attribute can be set in the following'
    ' ways:\n'
    '- provide the argument `space` on the command'
    ' line with a fully specified name\n'
    '- provide the argument `--project` on the command line\n'
    '- set the property `core/project`'
)


class SpaceResourceError(core_exceptions.Error):
  """Exception for errors related to Space resources."""


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class List(base.ListCommand):
  """List shared templates."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    group = parser.add_mutually_exclusive_group(
        required=True,
        help=_REQUIRED_FLAGS_BASE_TEXT,
    )
    group.add_argument(
        '--google-catalog',
        action='store_true',
        help=_GOOGLE_CATALOG_HELP_TEXT,
    )
    project_space_group = group.add_argument_group(
        'Specify --project and/or --space for custom shared templates.'
    )
    project_space_group.add_argument(
        '--project',
        help=_PROJECT_HELP_TEXT,
    )
    project_space_group.add_argument(
        '--space',
        required=True,
        help=_SPACE_HELP_TEXT,
    )
    parser.add_argument(
        '--location',
        required=False,
        help=_LOCATION_HELP_TEXT,
    )
    parser.display_info.AddFormat('yaml')
    parser.display_info.AddUriFunc(
        api_lib_utils.MakeGetUriFunc(
            'designcenter.projects.locations.spaces.sharedTemplates',
            release_track=base.ReleaseTrack.ALPHA,
        )
    )

  @staticmethod
  def ValidSpaceName(name):
    """Validates the space name."""
    pattern = re.compile(r'^projects/[^/]+/locations/[^/]+/spaces/[^/]+')
    return bool(pattern.match(name))

  def Run(self, args):
    """Run the list command."""
    client = apis.SharedTemplatesClient(release_track=base.ReleaseTrack.ALPHA)
    if args.google_catalog:
      if not args.IsSpecified('location'):
        raise SpaceResourceError(
            f'{_BASE_ERROR_MESSAGE}\n{_LOCATION_NOT_SPECIFIED_MESSAGE}'
        )
      project_id = api_lib_utils.GetGoogleCatalogProjectId()
      space_id = 'googlespace'
      parent = 'projects/{}/locations/{}/spaces/{}'.format(
          project_id, args.location, space_id
      )
    elif self.ValidSpaceName(args.space):
      if args.IsSpecified('location') or args.IsSpecified('project'):
        raise exceptions.ConflictingArgumentsException(
            '--location and --project cannot be used when a full resource name'
            ' is provided for --space.'
        )
      parent = args.space
    else:
      if not args.IsSpecified('location'):
        raise SpaceResourceError(
            f'{_BASE_ERROR_MESSAGE}\n{_LOCATION_NOT_SPECIFIED_MESSAGE}'
        )
      project_id = args.project or properties.VALUES.core.project.Get()
      if not project_id:
        raise SpaceResourceError(
            f'{_BASE_ERROR_MESSAGE}\n{_PROJECT_NOT_SPECIFIED_MESSAGE}'
        )
      space_id = args.space
      parent = 'projects/{}/locations/{}/spaces/{}'.format(
          project_id, args.location, space_id
      )
    return client.List(
        parent=parent, limit=args.limit, page_size=args.page_size
    )
