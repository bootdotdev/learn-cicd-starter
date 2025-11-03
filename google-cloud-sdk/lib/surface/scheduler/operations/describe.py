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
"""`gcloud scheduler operations describe` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.scheduler import GetApiAdapter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scheduler import util
from googlecloudsdk.core import resources


@base.DefaultUniverseOnly
class Describe(base.DescribeCommand):
  """Show the latest status of an operation."""
  detailed_help = {
      'DESCRIPTION': """\
          {description}
          """,
      'EXAMPLES': """\
          To describe the latest status of an operation:

              $ {command} projects/my-project/locations/us-central1/operations/my-operation
         """,
  }

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--name',
        help=(
            'The full name of the Cloud Scheduler operation to describe.'
            ' Format:'
            ' projects/{project}/locations/{location}/operations/{operation}'
        ),
        required=True,
    )

  def Run(self, args):
    operations_client = GetApiAdapter(self.ReleaseTrack()).operations
    operation_ref = resources.REGISTRY.Parse(
        args.name,
        collection=util.OPERATIONS_COLLECTION,
    )
    return operations_client.Get(operation_ref)
