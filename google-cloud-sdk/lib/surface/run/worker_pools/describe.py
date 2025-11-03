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
"""Command for obtaining details about a given worker-pool."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import connection_context
from googlecloudsdk.command_lib.run import exceptions
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import resource_args
from googlecloudsdk.command_lib.run import serverless_operations
from googlecloudsdk.command_lib.run.printers import export_printer
from googlecloudsdk.command_lib.run.printers import worker_pool_printer
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.command_lib.util.concepts import presentation_specs
from googlecloudsdk.core.resource import resource_printer


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Describe(base.Command):
  """Obtain details about a given worker-pool."""

  detailed_help = {
      'DESCRIPTION': """\
          {description}
          """,
      'EXAMPLES': """\
          To obtain details about a given worker-pool:

              $ {command} <worker-pool-name>

          To get those details in the YAML format:

              $ {command} <worker-pool-name> --format=yaml

          To get them in YAML format suited to export (omitting metadata
          specific to this deployment and status info):

              $ {command} <worker-pool-name> --format=export
          """,
  }

  @staticmethod
  def CommonArgs(parser):
    flags.AddRegionArg(parser)
    worker_pool_presentation = presentation_specs.ResourcePresentationSpec(
        'WORKER_POOL',
        resource_args.GetV1WorkerPoolResourceSpec(),
        'WorkerPool to describe.',
        required=True,
        prefixes=False,
    )
    concept_parsers.ConceptParser([worker_pool_presentation]).AddToParser(
        parser
    )

    resource_printer.RegisterFormatter(
        worker_pool_printer.WORKER_POOL_PRINTER_FORMAT,
        worker_pool_printer.WorkerPoolPrinter,
        hidden=True,
    )
    parser.display_info.AddFormat(
        worker_pool_printer.WORKER_POOL_PRINTER_FORMAT
    )
    resource_printer.RegisterFormatter(
        export_printer.EXPORT_PRINTER_FORMAT,
        export_printer.ExportPrinter,
        hidden=True,
    )

  @staticmethod
  def Args(parser):
    Describe.CommonArgs(parser)

  def _ConnectionContext(self, args):
    return connection_context.GetConnectionContext(
        args, flags.Product.RUN, self.ReleaseTrack()
    )

  def Run(self, args):
    """Obtain details about a given worker-pool."""
    conn_context = self._ConnectionContext(args)
    worker_pool_ref = args.CONCEPTS.worker_pool.Parse()
    flags.ValidateResource(worker_pool_ref)
    with serverless_operations.Connect(conn_context) as client:
      worker_pool = client.GetWorkerPool(worker_pool_ref)
    if not worker_pool:
      raise exceptions.ArgumentError('Cannot find worker pool [{}]'.format(
          worker_pool_ref.workerpoolsId))
    return worker_pool
