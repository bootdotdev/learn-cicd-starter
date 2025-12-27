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
"""`gcloud dataplex glossaries categories create` command."""
from googlecloudsdk.api_lib.dataplex import glossary
from googlecloudsdk.api_lib.dataplex import util as dataplex_util
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataplex import resource_args
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Create(base.Command):
  """Creates a glossary category.

  A glossary category represents a collection of glossary categories and
  glossary terms within a glossary that are related to each other.
  """

  detailed_help = {
      'EXAMPLES': """\

          To create a glossary category `test-category` in glossary `test-glossary` in project `test-project` in
          location `us-central1`, with description `test description`,
          displayName `displayName` and parent `projects/test-project/locations/us-central1/glossaries/test-glossary` , run:

            $ {command} test-category --glossary=test-glossary
            --location=us-central1 --project=test-project
            --parent='projects/test-project/locations/us-central1/glossaries/test-glossary'
            --description='test description' --display-name='displayName'

          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddGlossaryCategoryResourceArg(parser, 'to create.')
    parser.add_argument(
        '--display-name',
        required=False,
        help='Display name of the glossary category.',
    )
    parser.add_argument(
        '--description',
        required=False,
        help='Description of the glossary category.',
    )
    parser.add_argument(
        '--parent',
        required=True,
        help='Immediate parent of the created glossary category.',
    )
    labels_util.AddCreateLabelsFlags(parser)

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args):
    glossary_category_ref = args.CONCEPTS.glossary_category.Parse()
    dataplex_client = dataplex_util.GetClientInstance()
    create_response = dataplex_client.projects_locations_glossaries_categories.Create(
        dataplex_util.GetMessageModule().DataplexProjectsLocationsGlossariesCategoriesCreateRequest(
            categoryId=glossary_category_ref.Name(),
            parent=glossary_category_ref.Parent().RelativeName(),
            googleCloudDataplexV1GlossaryCategory=glossary.GenerateGlossaryCategoryForCreateRequest(
                args
            ),
        )
    )

    log.CreatedResource(
        create_response.name,
        details=(
            'Glossary category created in project [{0}] in location [{1}] in'
            ' glossary [{2}]'.format(
                glossary_category_ref.projectsId,
                glossary_category_ref.locationsId,
                glossary_category_ref.glossariesId,
            )
        ),
    )
    return create_response
