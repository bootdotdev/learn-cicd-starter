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
"""Command to describe a shared template revision."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import re

from googlecloudsdk.api_lib.design_center import shared_template_revisions as apis
from googlecloudsdk.api_lib.design_center import utils as api_lib_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.core import exceptions as core_exceptions
from googlecloudsdk.core import properties

_DETAILED_HELP = {
    'DESCRIPTION': 'Describe a shared template revision.',
    'EXAMPLES': """ \
        To describe the shared template revision `my-revision` in shared template `my-shared-template`, space `my-space`, project `my-project` and location `us-central1`, run:

          $ {command} my-revision --shared-template=my-shared-template --space=my-space --project=my-project --location=us-central1

        Or run:

          $ {command} projects/my-project/locations/us-central1/spaces/my-space/sharedTemplates/my-shared-template/revisions/my-revision

        To describe a shared template revision `my-revision` in shared template `google-template` from the Google Catalog and location `us-central1`, run:

          $ {command} my-revision --shared-template=google-template --google-catalog --location=us-central1
        """,
    'API REFERENCE': """ \
        This command uses the designcenter/v1alpha API. The full documentation for
        this API can be found at:
        http://cloud.google.com/application-design-center/docs
        """,
}

_BASE_ERROR_MESSAGE = 'Error parsing [revision].'

_LOCATION_NOT_SPECIFIED_MESSAGE = (
    'The [revision] resource is not properly specified.\n'
    'Failed to find attribute [location]. The attribute can be set in the'
    ' following ways:\n'
    '- provide the argument `revision` on the command line with a fully'
    ' specified name\n'
    '- provide the argument `--location` on the command line'
)

_PROJECT_NOT_SPECIFIED_MESSAGE = (
    'The [revision] resource is not properly specified.\n'
    'Failed to find attribute [project]. [project] must be specified unless'
    ' using --google-catalog, a full resource name, or the core/project'
    ' property is set. The attribute can be set in the following'
    ' ways:\n'
    '- provide the argument `revision` on the command line with a fully'
    ' specified name\n'
    '- provide the argument `--project` on the command line\n'
    '- set the property `core/project`'
)

_SPACE_NOT_SPECIFIED_MESSAGE = (
    'The [revision] resource is not properly specified.\n'
    'Failed to find attribute [space]. [space] must be specified unless'
    ' using --google-catalog or a full resource name. The attribute can'
    ' be set in the following ways:\n'
    '- provide the argument `revision` on the command line with a fully'
    ' specified name\n'
    '- provide the argument `--space` on the command line'
)

_SHARED_TEMPLATE_NOT_SPECIFIED_MESSAGE = (
    'The [revision] resource is not properly specified.\n'
    'Failed to find attribute [shared-template]. The attribute can'
    ' be set in the following ways:\n'
    '- provide the argument `revision` on the command line with a fully'
    ' specified name\n'
    '- provide the argument `--shared-template` on the command line'
)

_REVISION_HELP_TEXT = (
    'ID of the revision or fully qualified identifier for the'
    ' sharedTemplateRevision. Format:'
    ' projects/$project/locations/$location/spaces/$space/sharedTemplates/$sharedTemplate/revisions/$revision\n'
    ' To set the revision attribute:\n'
    '  * provide the fully qualified identifier `revision` on the command'
    ' line;\n'
    '  * provide the argument `revision` which represents the revision id'
    ' and the other arguments `--shared-template`, `--location`, `--project`,'
    ' `--space` or `--google-catalog` on the command line.'
)

_SHARED_TEMPLATE_HELP_TEXT = (
    'The sharedTemplate id of the revision resource.\n\n'
    'To set the shared-template attribute:\n'
    '  * provide the argument `revision` on the command line with a fully'
    ' specified name;\n'
    '  * provide the argument `--shared-template` on the command line.'
)

_LOCATION_HELP_TEXT = (
    'The location id of the revision resource.\n\n'
    'To set the location attribute:\n'
    '  * provide the argument `revision` on the command line with a fully'
    ' specified name;\n'
    '  * provide the argument `--location` on the command line.'
)

_PROJECT_HELP_TEXT = (
    'The project id of the revision resource.\n\n'
    'To set the project attribute:\n'
    '  * provide the argument `revision` on the command line with a fully'
    ' specified name;\n'
    '  * provide the argument `--project` on the command line;\n'
    '  * set the property `core/project`.'
)

_SPACE_HELP_TEXT = (
    'The space id of the revision resource.\n\n'
    'To set the space attribute:\n'
    '  * provide the argument `revision` on the command line with a fully'
    ' specified name;\n'
    '  * provide the argument `--space` on the command line.'
)

_GOOGLE_CATALOG_HELP_TEXT = (
    'If provided, describes a shared template revision from the Google Catalog.'
    ' This sets the project to "gcpdesigncenter" and space to'
    ' "googlespace".'
)


class SharedTemplateRevisionResourceError(core_exceptions.Error):
  """Exception for errors related to SharedTemplateRevision resources."""


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class DescribeAlpha(base.DescribeCommand):
  """Describe a shared template revision."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    # Positional argument for revision
    parser.add_argument(
        'revision',
        metavar='REVISION',
        help=_REVISION_HELP_TEXT,
    )
    # Shared template flag
    parser.add_argument(
        '--shared-template',
        required=False,
        help=_SHARED_TEMPLATE_HELP_TEXT,
    )
    # Location flag
    parser.add_argument(
        '--location',
        required=False,
        help=_LOCATION_HELP_TEXT,
    )

    # Argument group for --project/--space or --google-catalog
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--google-catalog',
        action='store_true',
        help=_GOOGLE_CATALOG_HELP_TEXT,
    )
    # Nested group for --project and --space
    project_space_group = group.add_argument_group(
        'Specify --project and --space for custom shared templates.'
    )
    project_space_group.add_argument(
        '--project',
        required=False,
        help=_PROJECT_HELP_TEXT,
    )
    project_space_group.add_argument(
        '--space',
        required=False,
        help=_SPACE_HELP_TEXT,
    )

  @staticmethod
  def ValidSharedTemplateRevisionName(name):
    """Validates the shared template revision name."""
    pattern = re.compile(
        r'^projects/[^/]+/locations/[^/]+/spaces/[^/]+/sharedTemplates/[^/]+/revisions(/[^/]+)?$'
    )
    return pattern.match(name) is not None

  def Run(self, args):
    """Run the describe command."""
    client = apis.SharedTemplateRevisionsClient(
        release_track=base.ReleaseTrack.ALPHA
    )

    # If the full resource name is provided, use it directly.
    if self.ValidSharedTemplateRevisionName(args.revision):
      if (
          args.IsSpecified('shared_template')
          or args.IsSpecified('location')
          or args.IsSpecified('project')
          or args.IsSpecified('space')
          or args.google_catalog
      ):
        raise exceptions.ConflictingArgumentsException(
            '--shared-template, --location, --project, --space, and'
            ' --google-catalog cannot be used when a full resource name is'
            ' provided.'
        )
      return client.Describe(name=args.revision)

    # Otherwise, build the resource name from flags.
    if not args.IsSpecified('location'):
      raise SharedTemplateRevisionResourceError(
          f'{_BASE_ERROR_MESSAGE}\n{_LOCATION_NOT_SPECIFIED_MESSAGE}'
      )
    location_id = args.location

    if args.google_catalog:
      project_id = api_lib_utils.GetGoogleCatalogProjectId()
      space_id = 'googlespace'
    else:
      project_id = args.project or properties.VALUES.core.project.Get()
      if not project_id:
        raise SharedTemplateRevisionResourceError(
            f'{_BASE_ERROR_MESSAGE}\n{_PROJECT_NOT_SPECIFIED_MESSAGE}'
        )
      if not args.IsSpecified('space'):
        raise SharedTemplateRevisionResourceError(
            f'{_BASE_ERROR_MESSAGE}\n{_SPACE_NOT_SPECIFIED_MESSAGE}'
        )
      space_id = args.space

    if not args.IsSpecified('shared_template'):
      raise SharedTemplateRevisionResourceError(
          f'{_BASE_ERROR_MESSAGE}\n{_SHARED_TEMPLATE_NOT_SPECIFIED_MESSAGE}'
      )
    shared_template_id = args.shared_template

    # Construct the resource name:
    # projects/{p}/locations/{l}/spaces/{s}/sharedTemplates/{st}/revisions/{str}
    shared_template_revision_name = (
        'projects/{}/locations/{}/spaces/{}/sharedTemplates/{}/revisions/{}'
        .format(
            project_id, location_id, space_id, shared_template_id, args.revision
        )
    )

    return client.Describe(name=shared_template_revision_name)
