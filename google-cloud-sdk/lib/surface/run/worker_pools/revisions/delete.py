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
"""Command for deleting a worker pool revision."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import exceptions
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import pretty_print
from googlecloudsdk.command_lib.run import resource_args
from googlecloudsdk.command_lib.run.v2 import deletion
from googlecloudsdk.command_lib.run.v2 import worker_pools_operations
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.command_lib.util.concepts import presentation_specs
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Delete(base.Command):
  """Delete a worker pool revision."""

  detailed_help = {
      'DESCRIPTION': """\
          {description}
          """,
      'EXAMPLES': """\
          To delete a revision `rev1` of a worker pool `worker1` in us-central1:

              $ {command} rev1 --region=us-central1 --workerpool=worker1
          """,
  }

  @staticmethod
  def CommonArgs(parser):
    revision_presentation = presentation_specs.ResourcePresentationSpec(
        'WORKER_POOL_REVISION',
        resource_args.GetV2WorkerPoolRevisionResourceSpec(prompt=True),
        'Worker pool revision to delete.',
        required=True,
        prefixes=False,
    )
    concept_parsers.ConceptParser([revision_presentation]).AddToParser(parser)
    # TODO(b/366115709): Add WorkerPoolRevision printer.
    flags.AddAsyncFlag(parser)

  @staticmethod
  def Args(parser):
    Delete.CommonArgs(parser)

  def Run(self, args):
    """Delete a worker pool revision."""

    def DeriveRegionalEndpoint(endpoint):
      region = args.CONCEPTS.worker_pool_revision.Parse().locationsId
      return region + '-' + endpoint

    worker_pool_revision_ref = args.CONCEPTS.worker_pool_revision.Parse()
    flags.ValidateResource(worker_pool_revision_ref)
    console_io.PromptContinue(
        message='Revision [{revision}] will be deleted.'.format(
            revision=worker_pool_revision_ref.revisionsId
        ),
        throw_if_unattended=True,
        cancel_on_no=True,
    )
    run_client = apis.GetGapicClientInstance(
        'run', 'v2', address_override_func=DeriveRegionalEndpoint
    )
    worker_pools_client = worker_pools_operations.WorkerPoolsOperations(
        run_client
    )

    def DeleteWithExistenceCheck(worker_pool_revision_ref):
      response = worker_pools_client.DeleteRevision(worker_pool_revision_ref)
      if not response:
        raise exceptions.ArgumentError(
            'Cannot find revision [{revision}] under worker pool'
            ' [{worker_pool}] in region [{region}]'.format(
                revision=worker_pool_revision_ref.revisionsId,
                worker_pool=worker_pool_revision_ref.workerPoolsId,
                region=worker_pool_revision_ref.locationsId,
            )
        )

    # TODO: b/390067647 - Use response.result() once the issue is fixed
    deletion.Delete(
        worker_pool_revision_ref,
        worker_pools_client.GetRevision,
        DeleteWithExistenceCheck,
        args.async_,
    )

    if args.async_:
      pretty_print.Success(
          'Revision [{}] is being deleted.'.format(
              worker_pool_revision_ref.revisionsId
          )
      )
    else:
      log.DeletedResource(worker_pool_revision_ref.revisionsId, 'revision')
