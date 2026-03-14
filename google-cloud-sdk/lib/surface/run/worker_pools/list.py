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
"""Command for listing available worker-pools."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.run import global_methods
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import commands
from googlecloudsdk.command_lib.run import connection_context
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import pretty_print
from googlecloudsdk.command_lib.run import resource_args
from googlecloudsdk.command_lib.run import serverless_operations
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.command_lib.util.concepts import presentation_specs


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class List(commands.List):
  """List available worker-pools."""

  detailed_help = {
      'DESCRIPTION': """\
          {description}
          """,
      'EXAMPLES': """\
          To list available worker-pools:

              $ {command}
          """,
  }

  @classmethod
  def CommonArgs(cls, parser):
    # Flags specific to connecting to a cluster
    project_presentation = presentation_specs.ResourcePresentationSpec(
        '--project',
        resource_args.GetNamespaceResourceSpec(),
        'Project to list worker-pools in.',
        required=True,
        prefixes=False,
        hidden=True,
    )
    flags.AddRegionArg(parser)
    concept_parsers.ConceptParser([project_presentation]).AddToParser(parser)
    parser.display_info.AddFormat(
        'table('
        '{ready_column},'
        'name:label=WORKER_POOL,'
        'region:label=REGION,'
        'last_modifier:label="LAST DEPLOYED BY",'
        'last_transition_time:label="LAST DEPLOYED AT",'
        'author:label="CREATED BY",'
        'creation_timestamp:label=CREATED):({alias})'.format(
            ready_column=pretty_print.READY_COLUMN,
            alias=commands.SATISFIES_PZS_ALIAS,
        )
    )
    parser.display_info.AddUriFunc(cls._GetResourceUri)

  @classmethod
  def Args(cls, parser):
    cls.CommonArgs(parser)

  def Run(self, args):
    """List available worker-pools."""
    # Use the mixer for global request if there's no --region flag.
    project_ref = args.CONCEPTS.project.Parse()
    if not args.IsSpecified('region'):
      client = global_methods.GetServerlessClientInstance(api_version='v1')
      self.SetPartialApiEndpoint(client.url)
      # Don't consider region property here, we'll default to all regions
      return commands.SortByName(
          global_methods.ListWorkerPools(client, project_ref)
      )

    conn_context = connection_context.GetConnectionContext(
        args, flags.Product.RUN, self.ReleaseTrack()
    )
    with serverless_operations.Connect(conn_context) as client:
      self.SetCompleteApiEndpoint(conn_context.endpoint)
      return commands.SortByName(client.ListWorkerPools(project_ref))
