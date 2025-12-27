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
"""`gcloud dataplex entries update` command."""

from googlecloudsdk.api_lib.dataplex import entry as entry_api
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import parser_arguments
from googlecloudsdk.calliope import parser_extensions
from googlecloudsdk.command_lib.dataplex import flags
from googlecloudsdk.command_lib.dataplex import resource_args


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Update(base.UpdateCommand):
  """Update a Dataplex Entry."""

  detailed_help = {
      'DESCRIPTION': 'Update specified fields in a given Dataplex Entry.',
      'EXAMPLES': """\
          To update fully qualified name (FQN) of an entry, run:

            $ {command} entry1 --project=test-project --location=us-central1 --entry-group entry-group1 --fully-qualified-name='custom:a.b.c'

          To update description of an entry, run:

            $ {command} entry1 --project=test-project --location=us-central1 --entry-group entry-group1 --entry-source-description='Updated description' --entry-source-update-time='1998-09-04T12:00:00-0700'

          To clear the description of an entry, run:

            $ {command} entry1 --project=test-project --location=us-central1 --entry-group entry-group1 --clear-entry-source-description --entry-source-update-time='1998-09-04T12:00:00-0700'

          To add or update aspects from the YAML/JSON file, run:

            $ {command} entry1 --project=test-project --location=us-central1 --entry-group entry-group1 --update-aspects=path-to-a-file-with-aspects.json

          To remove all aspects of type `test-project.us-central1.some-aspect-type` from the entry, run:

            $ {command} entry1 --project=test-project --location=us-central1 --entry-group entry-group1 --remove-aspects='test-project.us-central1.some-aspect-type@*'

          To remove all aspects on path `Schema.column1` from the entry, run:

            $ {command} entry1 --project=test-project --location=us-central1 --entry-group entry-group1 --remove-aspects='*@Schema.column1'

          To remove exact aspects `test-project.us-central1.some-aspect-type@Schema.column1` and `test-project.us-central1.some-aspect-type2@Schema.column2` from the entry, run:

            $ {command} entry1 --project=test-project --location=us-central1 --entry-group entry-group1 --remove-aspects=test-project.us-central1.some-aspect-type@Schema.column1,test-project.us-central2.some-aspect-type@Schema.column2

          """,
  }

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor):
    resource_args.AddEntryResourceArg(parser)

    fully_qualified_name = parser.add_mutually_exclusive_group()
    fully_qualified_name.add_argument(
        '--fully-qualified-name',
        help=(
            'FQN, a name for the entry that can reference it in an external'
            ' system.'
        ),
    )
    fully_qualified_name.add_argument(
        '--clear-fully-qualified-name',
        action='store_true',
        help='Clear the FQN for the Entry.',
    )

    flags.AddEntrySourceArgs(parser, for_update=True)
    flags.AddAspectFlags(parser)

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args: parser_extensions.Namespace):
    return entry_api.Update(args)
