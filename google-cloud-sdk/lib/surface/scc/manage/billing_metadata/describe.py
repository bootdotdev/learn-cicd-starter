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
"""Command to get the billing metadata."""

from googlecloudsdk.api_lib.scc.manage.billing_metadata import clients
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scc.manage import constants
from googlecloudsdk.command_lib.scc.manage import flags
from googlecloudsdk.command_lib.scc.manage import parsing


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Describe(base.DescribeCommand):
  """Get the billing metadata for a specific resource.

  Get the billing metadata for a given Google Cloud resource,
  including the associated billing account, cost-related settings, and
  other relevant information.

  ## EXAMPLES

  To get the details of a billing metadata for organization `123`, run:

    $ {command} --organization=123

  To get the details of a billing metadata for project `456`, run:

    $ {command} --project=456

  You can also specify the parent more generally for organizations:

    $ {command} --parent=organizations/123

  Or you can specify the parent for projects:

    $ {command} --parent=projects/123
  """

  @staticmethod
  def Args(parser):
    flags.CreateFlagForParent(required=True).AddToParser(parser)

  def Run(self, args):
    name = parsing.GetModuleNamePathFromArgs(
        args, constants.CustomModuleType.BILLING_METADATA
    )

    client = clients.BillingMetadataClient()

    return client.Get(name)
