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
"""Implements command to create a migration workflow."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.bq import util as api_util
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.bq import command_utils
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Create(base.Command):
  """Create a migration workflow."""

  detailed_help = {
      'brief': 'create migration workflows',
      'DESCRIPTION': 'Create a migration workflow',
      'EXAMPLES': """\
          To create a migration workflow in EU synchronously based on a config file, run:

            $ {command} --location=EU --config-file=config_file.yaml --no-async
            """,
  }

  @staticmethod
  def Args(parser):
    base.ASYNC_FLAG.AddToParser(parser)
    parser.add_argument(
        '--location',
        help='Location of the migration workflow.',
        required=True,
    )
    parser.add_argument(
        '--config-file',
        help='Path to the migration workflows config file.',
        required=True,
    )

  def Run(self, args):
    client = api_util.GetMigrationApiClient()
    migration_service = client.projects_locations_workflows

    request_type = api_util.GetMigrationApiMessage(
        'BigquerymigrationProjectsLocationsWorkflowsCreateRequest'
    )
    request = request_type()

    project = args.project or properties.VALUES.core.project.Get(required=True)
    location = args.location
    migration_workflow = command_utils.GetResourceFromFile(
        args.config_file,
        api_util.GetMigrationApiMessage(
            'GoogleCloudBigqueryMigrationV2MigrationWorkflow'
        ),
    )
    request.parent = f'projects/{project}/locations/{location}'
    request.googleCloudBigqueryMigrationV2MigrationWorkflow = migration_workflow

    response = migration_service.Create(request)

    if args.async_:
      return response
    else:
      migration_workflow_ref = resources.REGISTRY.ParseRelativeName(
          response.name,
          collection='bigquerymigration.projects.locations.workflows',
      )
      poller = command_utils.BqMigrationWorkflowPoller(migration_service)
      response = waiter.WaitFor(
          poller=poller,
          operation_ref=migration_workflow_ref,
          message='Running migration workflow [{}]'.format(response.name),
      )

    return response
