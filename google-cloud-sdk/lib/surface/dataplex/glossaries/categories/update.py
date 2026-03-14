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
"""`gcloud dataplex glossaries categories update` command."""

from googlecloudsdk.api_lib.dataplex import glossary
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
  """Updates a glossary category."""

  detailed_help = {
      'EXAMPLES': """\
          To update display name, desciption and labels of glossary category
          `test-category` in glossary `test-glossary` in project `test-project`
          in location `us-central1`, run:

          $ {command} test-category --location=us-central1 --project=test-project
          --glossary=test-glossary --description='updated description'
          --display-name='updated displayName' --labels=key1=value1,key2=value2

          To update parent of glossary category `test-category` in glossary
          `test-glossary` in project `test-project` in location `us-central1`, run:

          $ {command} test-category --location=us-central1 --project=test-project
          --glossary=test-glossary --parent='projects/test-project/locations/us-central1/glossaries/updated-glossary'

          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddGlossaryCategoryResourceArg(parser, 'to update.')
    parser.add_argument(
        '--description',
        required=False,
        help='Description of the glossary category.',
    )
    parser.add_argument(
        '--display-name',
        required=False,
        help='Display Name of the glossary category.',
    )
    parser.add_argument(
        '--parent',
        required=False,
        help='Immediate parent of the created glossary category.',
    )
    labels_util.AddCreateLabelsFlags(parser)

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args):
    update_mask = glossary.GenerateCategoryUpdateMask(args)
    if len(update_mask) < 1:
      raise exceptions.HttpException(
          'Update command must specify at least one additional parameter to'
          ' change.'
      )

    glossary_category_ref = args.CONCEPTS.glossary_category.Parse()
    dataplex_client = dataplex_util.GetClientInstance()
    update_response = dataplex_client.projects_locations_glossaries_categories.Patch(
        dataplex_util.GetMessageModule().DataplexProjectsLocationsGlossariesCategoriesPatchRequest(
            name=glossary_category_ref.RelativeName(),
            updateMask=','.join(update_mask),
            googleCloudDataplexV1GlossaryCategory=glossary.GenerateGlossaryCategoryForUpdateRequest(
                args
            ),
        )
    )

    log.UpdatedResource(glossary_category_ref)
    return update_response
