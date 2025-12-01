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
"""Command to list the details of an SCC service."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.scc.manage.services import clients
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scc.manage import flags
from googlecloudsdk.command_lib.scc.manage import parsing


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.ALPHA)
class List(base.ListCommand):
  """List the details of Security Command Center services.

  List the details of Security Command Center services for the specified folder,
  project or organization. Services along with their corresponding module
  information is returned as the response.

  ## EXAMPLES

  To list the Security Center services for
  organization `123`, run:

  $ {command} --organization=organizations/123

  To list Security Center services for
  folder `456`, run:

  $ {command} --folder=folders/456

  To list Security Center services for
  project `789`, run:

  $ {command} --project=projects/789

  You can also specify the parent more generally:

  $ {command} --parent=organizations/123
  """

  @staticmethod
  def Args(parser):
    base.URI_FLAG.RemoveFromParser(parser)
    flags.CreateParentFlag(
        resource_name="Security Center service", required=True
    ).AddToParser(parser)

  def Run(self, args):
    parent = parsing.GetParentResourceNameFromArgs(args)
    page_size = args.page_size
    limit = args.limit

    client = clients.SecurityCenterServicesClient()

    return client.List(
        page_size=page_size,
        parent=parent,
        limit=limit,
    )
