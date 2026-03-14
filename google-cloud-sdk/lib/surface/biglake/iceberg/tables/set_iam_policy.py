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
"""Command to set the IAM policy for a BigLake Iceberg REST catalog table."""

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
  """Set the IAM policy for a BigLake Iceberg REST catalog table."""

  detailed_help = {
      'DESCRIPTION': ('Sets the IAM policy for a BigLake Iceberg REST catalog '
                      'table.'),
      'EXAMPLES': """\
          To set the IAM policy for the catalog `my-catalog`, namespace `my-namespace`, and table `my-table` with the policy in `policy.json` run:

            $ {command} my-table policy.json --catalog=my-catalog --namespace=my-namespace
          """,
  }

  @staticmethod
  def Args(parser):
    flags.AddTableResourceArg(parser, 'to set the IAM policy for')
    iam_util.AddArgForPolicyFile(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command."""
    client = util.GetClientInstance(self.ReleaseTrack())
    messages = util.GetMessagesModule(self.ReleaseTrack())

    project = args.project or properties.VALUES.core.project.Get(required=True)
    table_name = f'projects/{project}/catalogs/{args.catalog}/namespaces/{args.namespace}/tables/{args.table}'
    policy = iam_util.ParsePolicyFile(args.policy_file, messages.Policy)
    return client.projects_catalogs_namespaces_tables.SetIamPolicy(
        messages.BiglakeProjectsCatalogsNamespacesTablesSetIamPolicyRequest(
            resource=table_name,
            setIamPolicyRequest=messages.SetIamPolicyRequest(policy=policy),
        )
    )
