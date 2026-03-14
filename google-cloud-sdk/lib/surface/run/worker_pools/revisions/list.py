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
"""Command for listing available worker pool revisions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import commands
from googlecloudsdk.command_lib.run import connection_context
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import platforms
from googlecloudsdk.command_lib.run import pretty_print
from googlecloudsdk.command_lib.run import resource_args
from googlecloudsdk.command_lib.run import serverless_operations
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.command_lib.util.concepts import presentation_specs
from googlecloudsdk.core import log


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class List(commands.List):
  """List available worker pool revisions."""

  detailed_help = {
      'DESCRIPTION': """\
          {description}
          """,
      'EXAMPLES': """\
          To list all revisions in a worker pool `foo`:

              $ {command} --worker-pool=foo
          """,
  }

  @classmethod
  def CommonArgs(cls, parser):
    worker_pool_presentation = presentation_specs.ResourcePresentationSpec(
        '--namespace',
        resource_args.GetNamespaceResourceSpec(),
        'Namespace to list revisions in.',
        required=True,
        prefixes=False,
        hidden=True,
    )
    concept_parsers.ConceptParser([worker_pool_presentation]).AddToParser(
        parser
    )

    flags.AddWorkerPoolFlag(parser)
    flags.AddRegionArg(parser)

    parser.display_info.AddFormat(
        'table('
        '{ready_column},'
        'name:label=REVISION,'
        'active.yesno(yes="yes", no=""),'
        'worker_pool_name:label=WORKER_POOL:sort=1,'
        'creation_timestamp.date("%Y-%m-%d %H:%M:%S %Z"):'
        'label=DEPLOYED:sort=2:reverse,'
        'author:label="DEPLOYED BY"):({alias})'.format(
            ready_column=pretty_print.READY_COLUMN,
            alias=commands.SATISFIES_PZS_ALIAS,
        )
    )

  @classmethod
  def Args(cls, parser):
    cls.CommonArgs(parser)

  def _FilterServiceRevisions(self, revisions):
    """Filters out revisions that are service revisions.

    Per discussion with jmahood@, we want to make sure that all resources are
    self-contained, so none of the describe/list commands should mix the
    resource type.

    Args:
      revisions: List of revisions to filter.

    Returns:
      List of revisions that are worker pool revisions.
    """
    return list(filter(lambda rev: rev.worker_pool_name is not None, revisions))

  def Run(self, args):
    """List available revisions."""
    label_selector = None
    worker_pool_name = args.worker_pool
    conn_context = connection_context.GetConnectionContext(
        args, flags.Product.RUN, self.ReleaseTrack()
    )
    namespace_ref = args.CONCEPTS.namespace.Parse()
    with serverless_operations.Connect(conn_context) as client:
      self.SetCompleteApiEndpoint(conn_context.endpoint)
      if platforms.GetPlatform() != platforms.PLATFORM_MANAGED:
        location_msg = ' in [{}]'.format(conn_context.cluster_location)
        log.status.Print(
            'For cluster [{cluster}]{zone}:'.format(
                cluster=conn_context.cluster_name,
                zone=location_msg if conn_context.cluster_location else '',
            )
        )
      if worker_pool_name is not None:
        label_selector = 'run.googleapis.com/workerPool = {}'.format(
            worker_pool_name
        )
      for rev in self._FilterServiceRevisions(
          client.ListRevisions(
              namespace_ref, label_selector, args.limit, args.page_size
          )
      ):
        yield rev
