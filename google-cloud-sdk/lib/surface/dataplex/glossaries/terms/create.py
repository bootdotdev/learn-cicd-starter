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
"""`gcloud dataplex glossaries terms create` command."""
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
  """Creates a glossary term.

  A glossary term holds a rich text description that can be attached to entries
  or specific columns to enrich them.
  """

  detailed_help = {
      'EXAMPLES': """\

          To create a glossary term `test-term` in glossary `test-glossary` in project `test-project` in
          location `us-central1`, with description `test description`,
          displayName `displayName` and parent `projects/test-project/locations/us-central1/glossaries/test-glossary/categories/test-category` , run:

            $ {command} test-term --glossary=test-glossary
            --location=us-central1 --project=test-project
            --parent='projects/test-project/locations/us-central1/glossaries/test-glossary/categories/test-category'
            --description='test description' --display-name='displayName'

          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddGlossaryTermResourceArg(parser, 'to create.')
    parser.add_argument(
        '--display-name',
        required=False,
        help='Display name of the glossary term.',
    )
    parser.add_argument(
        '--description',
        required=False,
        help='Description of the glossary term.',
    )
    parser.add_argument(
        '--parent',
        required=True,
        help='Immediate parent of the created glossary term.',
    )
    labels_util.AddCreateLabelsFlags(parser)

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args):
    glossary_term_ref = args.CONCEPTS.glossary_term.Parse()
    dataplex_client = dataplex_util.GetClientInstance()
    create_response = dataplex_client.projects_locations_glossaries_terms.Create(
        dataplex_util.GetMessageModule().DataplexProjectsLocationsGlossariesTermsCreateRequest(
            termId=glossary_term_ref.Name(),
            parent=glossary_term_ref.Parent().RelativeName(),
            googleCloudDataplexV1GlossaryTerm=glossary.GenerateGlossaryTermForCreateRequest(
                args
            ),
        )
    )

    log.CreatedResource(
        create_response.name,
        details=(
            'Glossary term created in project [{0}] in location [{1}] in'
            ' glossary [{2}]'.format(
                glossary_term_ref.projectsId,
                glossary_term_ref.locationsId,
                glossary_term_ref.glossariesId,
            )
        ),
    )
    return create_response
