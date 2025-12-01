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
"""`gcloud dataplex entries update-aspects` command."""

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
class UpdateAspects(base.UpdateCommand):
  """Add or update aspects for a Dataplex Entry."""

  detailed_help = {
      'EXAMPLES': """\

          To add or update aspects for the Dataplex entry `entry1` within the entry group `entry-group1` in location `us-central1` from the YAML/JSON file, run:

            $ {command} entry1 --project=test-project --location=us-central1 --entry-group entry-group1 --aspects=path-to-a-file-with-aspects.json

          """,
  }

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor):
    resource_args.AddEntryResourceArg(parser)

    flags.AddAspectFlags(
        parser,
        update_aspects_name='aspects',
        remove_aspects_name=None,
        required=True,
    )

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args: parser_extensions.Namespace):
    # Under the hood we perorm UpdateEntry call affecting only aspects field.
    return entry_api.Update(args, update_aspects_arg_name='aspects')
