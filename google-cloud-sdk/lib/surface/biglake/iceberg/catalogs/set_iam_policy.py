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
"""Command to set the IAM policy for a BigLake Iceberg REST catalog."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.biglake import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.biglake import flags
from googlecloudsdk.command_lib.iam import iam_util
from googlecloudsdk.core import properties


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class SetIamPolicy(base.Command):
  """Set the IAM policy for a BigLake Iceberg REST catalog."""

  detailed_help = {
      'DESCRIPTION': 'Sets the IAM policy for a BigLake Iceberg REST catalog.',
      'EXAMPLES': """\
          To set the IAM policy for the catalog `my-catalog` with the policy in `policy.json` run:

            $ {command} my-catalog policy.json
          """,
  }

  @staticmethod
  def Args(parser):
    flags.AddCatalogResourceArg(parser, 'to set the IAM policy for')
    iam_util.AddArgForPolicyFile(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command."""
    client = util.GetClientInstance(self.ReleaseTrack())
    messages = util.GetMessagesModule(self.ReleaseTrack())

    project = args.project or properties.VALUES.core.project.Get(required=True)
    catalog_name = f'projects/{project}/catalogs/{args.catalog}'
    policy = iam_util.ParsePolicyFile(args.policy_file, messages.Policy)
    return client.projects_catalogs.SetIamPolicy(
        messages.BiglakeProjectsCatalogsSetIamPolicyRequest(
            resource=catalog_name,
            setIamPolicyRequest=messages.SetIamPolicyRequest(policy=policy),
        )
    )
