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
"""`gcloud dataplex entries remove-aspects` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

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
class RemoveAspects(base.UpdateCommand):
  """Remove aspects from a Dataplex Entry."""

  detailed_help = {
      'EXAMPLES': """\

          To remove all aspects of type `test-project.us-central1.some-aspect-type` from the entry, run:

            $ {command} entry1 --project=test-project --location=us-central1 --entry-group entry-group1 --keys='test-project.us-central1.some-aspect-type@*'

          To remove all aspects on path `Schema.column1` from the entry, run:

            $ {command} entry1 --project=test-project --location=us-central1 --entry-group entry-group1 --keys='*@Schema.column1'

          To remove exact aspects `test-project.us-central1.some-aspect-type@Schema.column1` and `test-project.us-central1.some-aspect-type2@Schema.column2` from the entry, run:

            $ {command} entry1 --project=test-project --location=us-central1 --entry-group entry-group1 --keys=test-project.us-central1.some-aspect-type@Schema.column1,test-project.us-central2.some-aspect-type@Schema.column2

          """,
  }

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor):
    resource_args.AddEntryResourceArg(parser)

    flags.AddAspectFlags(
        parser,
        update_aspects_name=None,
        remove_aspects_name='keys',
        required=True,
    )

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args: parser_extensions.Namespace):
    # Under the hood we perorm UpdateEntry call affecting only aspects field.
    return entry_api.Update(args, remove_aspects_arg_name='keys')
