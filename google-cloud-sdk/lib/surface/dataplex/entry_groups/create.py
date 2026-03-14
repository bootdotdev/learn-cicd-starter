# -*- coding: utf-8 -*- #
# Copyright 2024 Google Inc. All Rights Reserved.
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
"""`gcloud dataplex entry-groups create` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.dataplex import entry_group
from googlecloudsdk.api_lib.dataplex import util as dataplex_util
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataplex import resource_args
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Create(base.Command):
  """Create a Dataplex Entry Group.

     Entry Group acts as a logical container used to organize Entries.
  """

  detailed_help = {
      'EXAMPLES':
          """\

          To create Entry Group `test-entry-group` in project `test-dataplex` at location `us-central1`,
          with description `test description` and displayName `test display name`, run:

            $ {command} test-entry-group --location=us-central1 --project=test-project --description='test description' --display-name='test display name'

          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddDataplexEntryGroupResourceArg(parser,
                                                   'to create.')
    parser.add_argument(
        '--description',
        required=False,
        help='Description of the Entry Group.')
    parser.add_argument(
        '--display-name',
        required=False,
        help='Display name of the Entry Group.')
    async_group = parser.add_group(
        mutex=True,
        required=False)
    async_group.add_argument(
        '--validate-only',
        action='store_true',
        default=False,
        help='Validate the create action, but don\'t actually perform it.')
    base.ASYNC_FLAG.AddToParser(async_group)
    labels_util.AddCreateLabelsFlags(parser)

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.')

  def Run(self, args):
    entry_group_ref = args.CONCEPTS.entry_group.Parse()
    dataplex_client = dataplex_util.GetClientInstance()
    create_req_op = dataplex_client.projects_locations_entryGroups.Create(
        dataplex_util.GetMessageModule(
        ).DataplexProjectsLocationsEntryGroupsCreateRequest(
            entryGroupId=entry_group_ref.Name(),
            parent=entry_group_ref.Parent().RelativeName(),
            validateOnly=args.validate_only,
            googleCloudDataplexV1EntryGroup=entry_group
            .GenerateEntryGroupForCreateRequest(args)))

    validate_only = getattr(args, 'validate_only', False)
    if validate_only:
      log.status.Print('Validation complete.')
      return

    async_ = getattr(args, 'async_', False)
    if not async_:
      response = entry_group.WaitForOperation(create_req_op)
      log.CreatedResource(
          response.name,
          details='Entry Group created in project [{0}] with location [{1}]'
          .format(entry_group_ref.projectsId,
                  entry_group_ref.locationsId))
      return response

    log.status.Print(
        'Creating Entry Group [{0}] with operation [{1}].'.format(
            entry_group_ref, create_req_op.name))
    return create_req_op
