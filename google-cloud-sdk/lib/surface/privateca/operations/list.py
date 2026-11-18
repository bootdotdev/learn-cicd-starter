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
"""List operations for the Private CA API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

# from googlecloudsdk.api_lib.privateca import base as privateca_base
from googlecloudsdk.api_lib.privateca import operations
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope.concepts import concepts
from googlecloudsdk.command_lib.util.concepts import concept_parsers


def _GetOperationStatus(op):
  if op.get('error'):
    return 'FAILURE'
  if op.get('done'):
    return 'SUCCESS'
  return 'RUNNING'


def _GetLocationResourceSpec():
  return concepts.ResourceSpec(
      'privateca.projects.locations',
      resource_name='location',
      locationsId=concepts.ResourceParameterAttributeConfig(
          name='location',
          help_text='The location to list operations in.',
      ),
      projectsId=concepts.DEFAULT_PROJECT_ATTRIBUTE_CONFIG,
  )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.Hidden
class List(base.ListCommand):
  """List operations for the Private CA API."""

  detailed_help = {
      'DESCRIPTION': """\
          Returns completed, failed, and pending operations on the Private CA API
          in a given location.""",
      'EXAMPLES': """\
          To list all operations in a given location:

          $ {command} --location=us-west1

          To filter for a specific end time in a given location:

          $ {command} --location=us-west1 --filter="metadata.endTime>=2025-09-25T16:00:00Z"
          """,
  }

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser.ForResource(
        '--location',
        _GetLocationResourceSpec(),
        'The location to list operations in.',
        required=True).AddToParser(parser)
    parser.display_info.AddFormat(
        'table(name.segment(-1):label=ID, name.segment(-3):label=LOCATION,'
        ' metadata.createTime:label=START_TIME, status():label=STATUS)'
    )
    parser.display_info.AddTransforms({'status': _GetOperationStatus})

  def Run(self, args):
    """Runs the command."""
    location_ref = args.CONCEPTS.location.Parse()
    operations_list = operations.ListOperations(location_ref.locationsId)
    return operations_list
