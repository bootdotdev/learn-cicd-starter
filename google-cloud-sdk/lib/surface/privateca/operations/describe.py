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
"""Describe an operation for the Private CA API."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.privateca import operations
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope.concepts import concepts
from googlecloudsdk.command_lib.util.concepts import concept_parsers


def _GetOperationResourceSpec():
  return concepts.ResourceSpec(
      'privateca.projects.locations.operations',
      resource_name='operation',
      operationsId=concepts.ResourceParameterAttributeConfig(
          name='operation', help_text='The operation to describe.'
      ),
      locationsId=concepts.ResourceParameterAttributeConfig(
          name='location',
          help_text='The location of the operation to describe.',
      ),
      projectsId=concepts.DEFAULT_PROJECT_ATTRIBUTE_CONFIG,
  )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.Hidden
class Describe(base.DescribeCommand):
  """Describe an operation ran on the Private CA API."""

  detailed_help = {
      'DESCRIPTION': """\
          Get details about a Long Running Operation.
          """,
      'EXAMPLES': """\
          To describe an operation:

          $ {command} operation-12345 --location=us-west1
          """,
  }

  @staticmethod
  def Args(parser):
    concept_parsers.ConceptParser.ForResource(
        'operation',
        _GetOperationResourceSpec(),
        'The operation to describe.',
        required=True,
    ).AddToParser(parser)

  def Run(self, args):
    operation_ref = args.CONCEPTS.operation.Parse()
    return operations.GetOperation(operation_ref)
