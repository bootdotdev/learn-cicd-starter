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
"""`gcloud dataplex aspect-types update` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.dataplex import aspect_type
from googlecloudsdk.api_lib.dataplex import util as dataplex_util
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.dataplex import resource_args
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Update(base.Command):
  """Update a Dataplex Aspect Type."""

  detailed_help = {
      'EXAMPLES':
          """\

          To update Aspect Type `test-aspect-type` in project `test-project` at location `us-central1`,
          with description `updated description` and display name `updated display name`, run:

            $ {command} test-aspect-type --location=us-central1 --project=test-project --description='updated description'
            --display-name='updated display name'

          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddDataplexAspectTypeResourceArg(parser, 'to update.')
    parser.add_argument(
        '--description', required=False, help='Description of the Aspect Type.'
    )
    parser.add_argument(
        '--display-name',
        required=False,
        help='Display name of the Aspect Type.',
    )
    parser.add_argument(
        '--metadata-template-file-name',
        help='The name of the JSON or YAML file to define Metadata Template.')
    parser.add_argument(
        '--etag', required=False, help='etag value for particular Aspect Type.'
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
    update_mask = aspect_type.GenerateAspectTypeUpdateMask(args)
    if len(update_mask) < 1:
      raise exceptions.HttpException(
          'Update commands must specify at least one additional parameter to '
          'change.'
      )

    aspect_type_ref = args.CONCEPTS.aspect_type.Parse()
    dataplex_client = dataplex_util.GetClientInstance()
    update_req_op = dataplex_client.projects_locations_aspectTypes.Patch(
        dataplex_util.GetMessageModule(
        ).DataplexProjectsLocationsAspectTypesPatchRequest(
            name=aspect_type_ref.RelativeName(),
            validateOnly=args.validate_only,
            updateMask=u','.join(update_mask),
            googleCloudDataplexV1AspectType=aspect_type
            .GenerateAspectTypeForUpdateRequest(args)))

    validate_only = getattr(args, 'validate_only', False)
    if validate_only:
      log.status.Print('Validation complete.')
      return

    async_ = getattr(args, 'async_', False)
    if not async_:
      response = aspect_type.WaitForOperation(update_req_op)
      log.UpdatedResource(aspect_type_ref, details='Operation was successful.')
      return response

    log.status.Print(
        'Updating Aspect Type [{0}] with operation [{1}].'.format(
            aspect_type_ref, update_req_op.name))
    return update_req_op
