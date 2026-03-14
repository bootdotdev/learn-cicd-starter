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
"""`gcloud dataplex entry-types update` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.dataplex import entry_type
from googlecloudsdk.api_lib.dataplex import util as dataplex_util
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.dataplex import resource_args
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Update(base.Command):
  """Update a Dataplex Entry Type."""

  detailed_help = {
      'EXAMPLES':
          """\

          To update Entry Type `test-entry-type` in project `test-project` at location `us-central1`,
          with description `updated description` and display name `updated display name`, run:

            $ {command} test-entry-type --location=us-central1 --project=test-project --description='updated description'
            --display-name='updated display name'

          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddDataplexEntryTypeResourceArg(parser, 'to update.')
    parser.add_argument(
        '--description', required=False, help='Description of the Entry Type.'
    )
    parser.add_argument(
        '--display-name',
        required=False,
        help='Display name of the Entry Type.',
    )
    parser.add_argument(
        '--platform',
        required=False,
        help='The platform that Entries of this type belongs to.')
    parser.add_argument(
        '--system',
        required=False,
        help='The system that Entries of this type belongs to.')
    parser.add_argument(
        '--type-aliases',
        metavar='TYPE_ALIASES',
        default=[],
        required=False,
        type=arg_parsers.ArgList(),
        help='Indicates the class this Entry Type belongs to.')
    parser.add_argument(
        '--required-aspects',
        action='append',
        required=False,
        help='Required aspect type for the entry type.',
        type=arg_parsers.ArgDict(
            spec={
                'type': str
            },
            required_keys=['type'],
        )
    )
    parser.add_argument(
        '--etag', required=False, help='etag value for particular Entry Type.'
    )
    async_type = parser.add_group(mutex=True, required=False)
    async_type.add_argument(
        '--validate-only',
        action='store_true',
        default=False,
        help="Validate the update action, but don't actually perform it.",
    )
    base.ASYNC_FLAG.AddToParser(async_type)
    labels_util.AddCreateLabelsFlags(parser)

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args):
    update_mask = entry_type.GenerateEntryTypeUpdateMask(args)
    if len(update_mask) < 1:
      raise exceptions.HttpException(
          'Update commands must specify at least one additional parameter to '
          'change.'
      )

    entry_type_ref = args.CONCEPTS.entry_type.Parse()
    dataplex_client = dataplex_util.GetClientInstance()
    update_req_op = dataplex_client.projects_locations_entryTypes.Patch(
        dataplex_util.GetMessageModule(
        ).DataplexProjectsLocationsEntryTypesPatchRequest(
            name=entry_type_ref.RelativeName(),
            validateOnly=args.validate_only,
            updateMask=u','.join(update_mask),
            googleCloudDataplexV1EntryType=entry_type
            .GenerateEntryTypeForUpdateRequest(args)))

    validate_only = getattr(args, 'validate_only', False)
    if validate_only:
      log.status.Print('Validation complete.')
      return

    async_ = getattr(args, 'async_', False)
    if not async_:
      response = entry_type.WaitForOperation(update_req_op)
      log.UpdatedResource(entry_type_ref, details='Operation was successful.')
      return response

    log.status.Print(
        'Updating Entry Type [{0}] with operation [{1}].'.format(
            entry_type_ref, update_req_op.name))
    return update_req_op
