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

"""Command to list autonomous database backups."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import list_pager
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope.concepts import concepts
from googlecloudsdk.command_lib.util.concepts import concept_parsers

VERSION_MAP = {
    base.ReleaseTrack.ALPHA: 'v1alpha',
    base.ReleaseTrack.GA: 'v1',
}


def LocationAttributeConfig():
  return concepts.ResourceParameterAttributeConfig(
      name='location', help_text='The Cloud location for the {resource}.')


def GetLocationResourceSpec(resource_name='location'):
  return concepts.ResourceSpec(
      'oracledatabase.projects.locations',
      resource_name=resource_name,
      locationsId=LocationAttributeConfig(),
      projectsId=concepts.DEFAULT_PROJECT_ATTRIBUTE_CONFIG,
      disable_auto_completers=True)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class List(base.ListCommand):
  r"""List autonomous database backups.

  ## DESCRIPTION
    Lists all AutonomousDatabaseBackups for the specified
    AutonomousDatabase.

  ## EXAMPLES
  To list all backups for an AutonomousDatabase with id `my-instance` in the
  location `us-east4`, run:

      $ {command} --location=us-east4
          --filter='autonomous_database_id="my-instance"'
  """

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser.ForResource(
        '--location',
        GetLocationResourceSpec(),
        group_help='The location you want to list the connection profiles for.',
        required=True).AddToParser(parser)

    base.FILTER_FLAG.RemoveFromParser(parser)
    base.Argument(
        '--filter',
        metavar='EXPRESSION',
        require_coverage_in_tests=False,
        category=base.LIST_COMMAND_FLAGS,
        help="""\
        Apply a ADB filter in the format :
        --filter='autonomous_database_id="my-instance"'
        """,
    ).AddToParser(parser)

  def Run(self, args):
    """List autonomous database backups."""
    client = apis.GetClientInstance(
        'oracledatabase', VERSION_MAP[self.ReleaseTrack()])
    messages = apis.GetMessagesModule(
        'oracledatabase', VERSION_MAP[self.ReleaseTrack()])
    ref = args.CONCEPTS.location.Parse()
    server_filter = args.filter
    # TODO(b/366489468): Remap the filter logic so that it works for both client
    # and server side filter side.
    # args.filter needs to be set to '' because the response doesn't contains
    # autonomous_database_id in the response, so if the client side filter
    # is not empty, the output will be empty.
    args.filter = ''
    return list_pager.YieldFromList(
        client.projects_locations_autonomousDatabaseBackups,
        messages.OracledatabaseProjectsLocationsAutonomousDatabaseBackupsListRequest(
            parent=ref.RelativeName(),
            pageSize=args.page_size,
            filter=server_filter,
        ),
        batch_size=args.page_size,
        field='autonomousDatabaseBackups',
        limit=args.limit,
        batch_size_attribute='pageSize',
    )
