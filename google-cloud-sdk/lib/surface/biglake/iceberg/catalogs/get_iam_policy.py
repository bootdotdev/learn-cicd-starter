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
"""Command to get the IAM policy for a BigLake Iceberg REST catalog."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.biglake import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.biglake import flags
from googlecloudsdk.core import properties


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class GetIamPolicy(base.ListCommand):
  """Get the IAM policy for a BigLake Iceberg REST catalog."""

  detailed_help = {
      'DESCRIPTION': 'Gets the IAM policy for a BigLake Iceberg REST catalog.',
      'EXAMPLES': """\
          To get the IAM policy for the catalog `my-catalog` run:

            $ {command} my-catalog
          """,
  }

  @staticmethod
  def Args(parser):
    flags.AddCatalogResourceArg(parser, 'to get the IAM policy for')
    base.URI_FLAG.RemoveFromParser(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command."""
    client = util.GetClientInstance(self.ReleaseTrack())
    messages = util.GetMessagesModule(self.ReleaseTrack())

    project = args.project or properties.VALUES.core.project.Get(required=True)
    catalog_name = f'projects/{project}/catalogs/{args.catalog}'

    return client.projects_catalogs.GetIamPolicy(
        messages.BiglakeProjectsCatalogsGetIamPolicyRequest(
            resource=catalog_name
        )
    )
