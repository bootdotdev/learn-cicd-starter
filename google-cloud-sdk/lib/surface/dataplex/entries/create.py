# -*- coding: utf-8 -*- #
# Copyright 2024 Google LLC. All Rights Reserved.
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
"""Create command for Dataplex Catalog Entries Resource."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.dataplex import entry as entry_api
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataplex import flags
from googlecloudsdk.command_lib.dataplex import resource_args


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Create(base.CreateCommand):
  """Create a Dataplex Entry resource."""

  detailed_help = {
      'EXAMPLES': """\
          To create a Dataplex entry with name `my-dataplex-entry` in location
          `us-central1` in entry group `my-entry-group` and with entry type projects/my-project/locations/us-central1/entryTypes/my-type, run:

            $ {command} my-dataplex-entry --location=us-central1 --entry_group=my-entry-group --entry-type projects/my-project/locations/us-central1/entryTypes/my-type

          To create a Dataplex Entry with name `my-child-entry` and set its parent to an existing entry `my-parent-entry`, run:

            $ {command} my-child-entry --location=us-central1 --entry_group=my-entry-group --entry-type projects/my-project/locations/us-central1/entryTypes/my-type --parent-entry projects/my-project/locations/us-central1/entryGroups/my-entry-group/entries/my-parent-entry

          To create a Dataplex Entry with its description, display name, ancestors, labels and timestamps populated in its EntrySource, run:

            $ {command} my-entry --location=us-central1 --entry_group=my-entry-group --entry-type projects/my-project/locations/us-central1/entryTypes/my-type --entry-source-description 'This is a description of the Entry.' --entry-source-display-name 'display name' --entry-source-ancestors '{"type":"projects/my-project/locations/us-central1/entryTypes/some-type", "name":"projects/my-project/locations/us-central1/entryGroups/my-entry-group/entries/ancestor-entry"}, {"type":"projects/my-project/locations/us-central1/entryTypes/another-type", "name":"projects/my-project/locations/us-central1/entryGroups/my-entry-group/entries/another-ancestor-entry"}' --entry-source-labels key1=value1,key2=value2 --entry-source-create-time 2024-01-01T09:39:25.160173Z --entry-source-update-time 2024-01-01T09:39:25.160173Z

          To create a Dataplex Entry reading its aspects from a YAML file, run:

            $ {command} my-entry --location=us-central1 --entry_group=my-entry-group --entry-type projects/my-project/locations/us-central1/entryTypes/my-type --aspects aspects.yaml

          The file containing the aspects has the following format:

            my-project.us-central1.my-aspect-type:
              aspectType: my-project.us-central1.my-aspect-type
              createTime: "2024-01-01T09:39:25.160173Z"
              updateTime: "2024-01-01T09:39:25.160173Z"
              data:
                {}
          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddProjectArg(parser, 'to create the Entry.')
    resource_args.AddEntryResourceArg(parser)
    resource_args.AddEntryTypeResourceArg(parser)
    resource_args.AddParentEntryResourceArg(parser)

    parser.add_argument(
        '--fully-qualified-name',
        help=(
            'A name for the entry that can reference it in an external system.'
            ' The maximum size of the field is 4000 characters.'
        ),
    )
    flags.AddEntrySourceArgs(parser, for_update=False)
    flags.AddAspectFlags(
        parser, update_aspects_name='aspects', remove_aspects_name=None
    )

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args):
    return entry_api.Create(args)
