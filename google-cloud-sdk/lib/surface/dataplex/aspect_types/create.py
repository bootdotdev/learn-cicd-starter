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
"""`gcloud dataplex aspect-types create` command."""

from googlecloudsdk.api_lib.dataplex import aspect_type
from googlecloudsdk.api_lib.dataplex import util as dataplex_util
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataplex import resource_args
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Create(base.Command):
  """Create a Dataplex Aspect Type.

     Aspect Type is a template for creating Aspects.
  """

  detailed_help = {
      'EXAMPLES':
          """\

          To create Aspect Type `test-aspect-type` in project `test-dataplex` at location `us-central1`,
          with description `test description`, displayName `test display name` and metadataTemplateFileName `file.json`, run:

            $ {command} test-aspect-type --location=us-central1 --project=test-project --description='test description'
            --display-name='test display name'
            --metadata-template-file-name='file.json'

          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddDataplexAspectTypeResourceArg(parser,
                                                   'to create.')
    parser.add_argument(
        '--description',
        required=False,
        help='Description of the Aspect Type.')
    parser.add_argument(
        '--display-name',
        required=False,
        help='Display name of the Aspect Type.')
    parser.add_argument(
        '--metadata-template-file-name',
        required=True,
        help='The name of the JSON or YAML file to define Metadata Template.')
    parser.add_argument(
        '--data-classification',
        help='Data classification of the Aspect Type.',
        choices=['METADATA_AND_DATA'],
    )

    async_type = parser.add_group(
        mutex=True,
        required=False)
    async_type.add_argument(
        '--validate-only',
        action='store_true',
        default=False,
        help='Validate the create action, but don\'t actually perform it.')
    base.ASYNC_FLAG.AddToParser(async_type)
    labels_util.AddCreateLabelsFlags(parser)

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.')

  def Run(self, args):
    aspect_type_ref = args.CONCEPTS.aspect_type.Parse()
    dataplex_client = dataplex_util.GetClientInstance()
    create_req_op = dataplex_client.projects_locations_aspectTypes.Create(
        dataplex_util.GetMessageModule(
        ).DataplexProjectsLocationsAspectTypesCreateRequest(
            aspectTypeId=aspect_type_ref.Name(),
            parent=aspect_type_ref.Parent().RelativeName(),
            validateOnly=args.validate_only,
            googleCloudDataplexV1AspectType=aspect_type
            .GenerateAspectTypeForCreateRequest(args)))

    validate_only = getattr(args, 'validate_only', False)
    if validate_only:
      log.status.Print('Validation complete.')
      return

    async_ = getattr(args, 'async_', False)
    if not async_:
      response = aspect_type.WaitForOperation(create_req_op)
      log.CreatedResource(
          response.name,
          details='Aspect Type created in project [{0}] with location [{1}]'
          .format(aspect_type_ref.projectsId,
                  aspect_type_ref.locationsId))
      return response

    log.status.Print(
        'Creating Aspect Type [{0}] with operation [{1}].'.format(
            aspect_type_ref, create_req_op.name))
    return create_req_op
