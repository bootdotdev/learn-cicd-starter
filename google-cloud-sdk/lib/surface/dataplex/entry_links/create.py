# -*- coding: utf-8 -*- #
# Copyright 2025 Google LLC. All Rights Reserved.
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
"""Create a Dataplex Entry Link."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.dataplex import entry_link
from googlecloudsdk.api_lib.dataplex import util as dataplex_util
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.dataplex import resource_args
from googlecloudsdk.core import log
from googlecloudsdk.core import yaml


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Create(base.Command):
  """Create a Dataplex Entry Link."""

  detailed_help = {
      'EXAMPLES': """\
To create a Dataplex Entry Link, you need to provide the entry link ID, the
entry group, the location, the project, the entry link type, and a path to a
YAML file containing the entry references. The entry references file should
contain a list of dictionaries, each representing an entry reference.

For example, to create an entry link of entry link type
'projects/655216118709/locations/global/entryLinkTypes/synonym' named
'my-entry-link' using entry references from 'entry_references.yaml', run:

        $ {command} my-entry-link \\
          --entry-group=my-entry-group \\
          --location=us-central1 \\
          --project=test-project \\
          --entry-link-type=projects/655216118709/locations/global/entryLinkTypes/synonym \\
          --entry-references=path/to/entry_references.yaml

Example of entry_references.yaml file:
```yaml
  - name: projects/test-project/locations/us-central1/entryGroups/my-entry-group/entries/my-entry-1
    type: SOURCE
    path: my_path
  - name: projects/test-project/locations/us-central1/entryGroups/my-entry-group/entries/my-entry-2
    type: TARGET
```
          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddDataplexEntryLinkResourceArg(parser, 'to create.')
    parser.add_argument(
        '--entry-link-type',
        required=True,
        help=(
            'Required. The type of the entry link. It is a resource name of the'
            ' EntryLinkType. Example:'
            ' `projects/my-project/locations/global/entryLinkTypes/my-link-type`'
        ),
    )
    parser.add_argument(
        '--entry-references',
        type=str,
        required=True,
        help=(
            'Required. Path to a YAML or JSON file containing the entry'
            ' references. The file should contain a list of dictionaries, each'
            ' with "name", "type", and optional "path" keys. Example:\n'
            '  -\n'
            '    name: projects/test-project/locations/us-central1/entryGroups/'
            'my-entry-group/entries/my-entry-1\n'
            '    type: SOURCE\n'
            '    path: my_path\n'
            '  -\n'
            '    name: projects/test-project/locations/us-central1/entryGroups/'
            'my-entry-group/entries/my-entry-2\n'
            '    type: TARGET'
        ),
    )

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args):
    entry_link_ref = args.CONCEPTS.entry_link.Parse()
    # Read and parse the entry_references.yaml file
    try:
      entry_references_content = yaml.load_path(args.entry_references)
    except yaml.Error as e:
      raise exceptions.BadFileException(
          'entry-references', f'Error parsing YAML file: {e}'
      )
    if not entry_references_content:
      raise exceptions.BadFileException(
          'entry-references', 'The entry references file is empty.'
      )

    # Create the list of entry references objects
    entry_references_message = entry_link.CreateEntryReferences(
        entry_references_content=entry_references_content
    )

    dataplex_client = dataplex_util.GetClientInstance()
    entry_link_response = dataplex_client.projects_locations_entryGroups_entryLinks.Create(
        dataplex_util.GetMessageModule().DataplexProjectsLocationsEntryGroupsEntryLinksCreateRequest(
            entryLinkId=entry_link_ref.Name(),
            parent=entry_link_ref.Parent().RelativeName(),
            googleCloudDataplexV1EntryLink=dataplex_util.GetMessageModule().GoogleCloudDataplexV1EntryLink(
                entryLinkType=args.entry_link_type,
                entryReferences=entry_references_message,
                name=entry_link_ref.RelativeName(),
            ),
        )
    )
    log.CreatedResource(
        entry_link_response.name,
        details=(
            'Content entry link in project [{0}] with location [{1}] in entry'
            ' group [{2}]'.format(
                entry_link_ref.projectsId,
                entry_link_ref.locationsId,
                entry_link_ref.entryGroupsId,
            )
        ),
    )
