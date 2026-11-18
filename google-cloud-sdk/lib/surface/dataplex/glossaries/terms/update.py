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
"""`gcloud dataplex glossaries terms update` command."""

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
  """Updates a glossary term."""

  detailed_help = {
      'EXAMPLES': """\
          To update display name, desciption and labels of glossary term
          `test-term` in glossary `test-glossary` in project `test-project`
          in location `us-central1`, run:

          $ {command} test-term --location=us-central1 --project=test-project
          --glossary=test-glossary --description='updated description'
          --display-name='updated displayName' --labels=key1=value1,key2=value2

          To update parent of glossary term `test-term` in glossary
          `test-glossary` in project `test-project` in location `us-central1`, run:

          $ {command} test-term --location=us-central1 --project=test-project
          --glossary=test-glossary --parent='projects/test-project/locations/us-central1/glossaries/updated-glossary'

          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddGlossaryTermResourceArg(parser, 'to update.')
    parser.add_argument(
        '--description',
        required=False,
        help='Description of the glossary term.',
    )
    parser.add_argument(
        '--display-name',
        required=False,
        help='Display name of the glossary term.',
    )
    parser.add_argument(
        '--parent',
        required=False,
        help='Immediate parent of the created glossary term.',
    )
    labels_util.AddCreateLabelsFlags(parser)

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args):
    update_mask = glossary.GenerateTermUpdateMask(args)
    if len(update_mask) < 1:
      raise exceptions.HttpException(
          'Update commands must specify at least one additional parameter to'
          ' change.'
      )

    glossary_term_ref = args.CONCEPTS.glossary_term.Parse()
    dataplex_client = dataplex_util.GetClientInstance()
    update_response = dataplex_client.projects_locations_glossaries_terms.Patch(
        dataplex_util.GetMessageModule().DataplexProjectsLocationsGlossariesTermsPatchRequest(
            name=glossary_term_ref.RelativeName(),
            updateMask=','.join(update_mask),
            googleCloudDataplexV1GlossaryTerm=glossary.GenerateGlossaryTermForUpdateRequest(
                args
            ),
        )
    )

    log.UpdatedResource(glossary_term_ref)
    return update_response
