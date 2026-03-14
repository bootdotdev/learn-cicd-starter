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
"""Command for obtaining details about a given worker pool revision."""


from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import connection_context
from googlecloudsdk.command_lib.run import exceptions
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import resource_args
from googlecloudsdk.command_lib.run import serverless_operations
from googlecloudsdk.command_lib.run.printers import export_printer
from googlecloudsdk.command_lib.run.printers import worker_pool_revision_printer
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.command_lib.util.concepts import presentation_specs
from googlecloudsdk.core.resource import resource_printer


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Describe(base.DescribeCommand):
  """Obtain details about a given worker pool revision."""

  detailed_help = {
      'DESCRIPTION': """\
          {description}
          """,
      'EXAMPLES': """\
          To describe a revision `rev.1` of a worker pool `worker1` in us-central1:

              $ {command} rev.1 --region=us-central1 --workerpool=worker1
          """,
  }

  @staticmethod
  def CommonArgs(parser):
    flags.AddRegionArg(parser)
    revision_presentation = presentation_specs.ResourcePresentationSpec(
        'WORKER_POOL_REVISION',
        resource_args.GetRevisionResourceSpec(is_worker_pool_revision=True),
        'Worker pool revision to describe.',
        required=True,
        prefixes=False,
    )
    concept_parsers.ConceptParser([revision_presentation]).AddToParser(parser)

    resource_printer.RegisterFormatter(
        worker_pool_revision_printer.REVISION_PRINTER_FORMAT,
        worker_pool_revision_printer.WorkerPoolRevisionPrinter,
        hidden=True,
    )
    parser.display_info.AddFormat(
        worker_pool_revision_printer.REVISION_PRINTER_FORMAT
    )
    resource_printer.RegisterFormatter(
        export_printer.EXPORT_PRINTER_FORMAT,
        export_printer.ExportPrinter,
        hidden=True,
    )

  @staticmethod
  def Args(parser):
    Describe.CommonArgs(parser)

  def Run(self, args):
    """Show details about a revision."""
    conn_context = connection_context.GetConnectionContext(
        args, flags.Product.RUN, self.ReleaseTrack()
    )
    revision_ref = args.CONCEPTS.worker_pool_revision.Parse()

    with serverless_operations.Connect(conn_context) as client:
      wrapped_revision = client.GetRevision(revision_ref)

    # If the revision is not a worker pool revision, we should not show it.
    if not wrapped_revision or wrapped_revision.worker_pool_name is None:
      raise exceptions.ArgumentError(
          'Cannot find revision [{}]'.format(revision_ref.revisionsId)
      )
    return wrapped_revision
