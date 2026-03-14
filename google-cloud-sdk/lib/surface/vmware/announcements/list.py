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
"""'vmware announcements list' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.vmware import announcements
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.vmware import flags


DETAILED_HELP = {
    'DESCRIPTION': """
          List announcements in a VMware Engine.
          """,
    'EXAMPLES': """
          To list maintanance announcements run:

            $ {command} --type=maintenance --location=us-west2-a --project=my-project

            Or:

            $ {command} --type=maintenance

          In the second example, the project and location are taken from gcloud properties core/project and compute/zone.
    """,
}


class _MissingKeyHandler(dict):

  def __missing__(self, key):
    return f'{{{{{key}}}}}'


def _value_or_default(metadata, key, default='N/A'):
  """Returns the value of the key in the metadata or the default value."""
  if metadata and key in metadata:
    return metadata[key]
  return default


def _format_description(resource):
  """Formats the description of the announcement."""
  description_template = (
      resource['description'].replace('{{', '{').replace('}}', '}')
  )
  description_args = _MissingKeyHandler(resource['metadata'])
  return description_template.format_map(description_args)


def _add_type_argument(parser):
  """Adds a type argument to filter the announcements list."""
  parser.add_argument(
      '--type',
      required=True,
      choices=['maintenance'],
      help='The type of announcement to list.',
  )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class List(base.ListCommand):
  """List announcements in a Google Cloud VMware Engine."""

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.AddLocationArgToParser(parser)
    _add_type_argument(parser)
    parser.display_info.AddTransforms({
        'value_or_default': _value_or_default,
        'format_description': _format_description,
    })
    parser.display_info.AddFormat(
        'table(name.segment(-1):label=NAME,'
        'name.segment(-3):label=LOCATION,'
        'metadata.value_or_default(target):label=TARGET,'
        'format_description():label=DESCRIPTION,'
        'code:label=CODE,'
        'metadata.value_or_default(upgrade_start_date):label=UPGRADE_START_DATE,'
        'metadata.value_or_default(upgrade_type):label=UPGRADE_TYPE,'
        'createTime)'
    )

  def Run(self, args):
    location = args.CONCEPTS.location.Parse()
    return announcements.AnnouncementsClient().List(location, args.type.upper())
