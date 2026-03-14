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
"""Command for updating instances split for worker-pool resource."""

from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import exceptions as serverless_exceptions
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import pretty_print
from googlecloudsdk.command_lib.run import resource_args
from googlecloudsdk.command_lib.run import stages
from googlecloudsdk.command_lib.run.printers.v2 import instance_split_printer
from googlecloudsdk.command_lib.run.v2 import config_changes as config_changes_mod
from googlecloudsdk.command_lib.run.v2 import flags_parser
from googlecloudsdk.command_lib.run.v2 import instance_split
from googlecloudsdk.command_lib.run.v2 import worker_pools_operations
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.command_lib.util.concepts import presentation_specs
from googlecloudsdk.core.console import progress_tracker
from googlecloudsdk.core.resource import resource_printer


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class AdjustInstanceSplit(base.Command):
  """Adjust the instance assignments for a Cloud Run worker-pool."""

  detailed_help = {
      'DESCRIPTION': """\
          {description}
          """,
      'EXAMPLES': """\
          To assign 10% of instances to revision my-worker-pool-s5sxn and
          90% of instances to revision my-worker-pool-cp9kw run:

              $ {command} my-worker-pool --to-revisions=my-worker-pool-s5sxn=10,my-worker-pool-cp9kw=90

          To increase the instances to revision my-worker-pool-s5sxn to 20% and
          by reducing the instances to revision my-worker-pool-cp9kw to 80% run:

              $ {command} my-worker-pool --to-revisions=my-worker-pool-s5sxn=20

          To rollback to revision my-worker-pool-cp9kw run:

              $ {command} my-worker-pool --to-revisions=my-worker-pool-cp9kw=100

          To assign 100% of instances to the current or future LATEST revision
          run:

              $ {command} my-worker-pool --to-latest

          You can also refer to the current or future LATEST revision in
          --to-revisions by the string "LATEST". For example, to set 10% of
          instances to always float to the latest revision:

              $ {command} my-worker-pool --to-revisions=LATEST=10

         """,
  }

  @classmethod
  def CommonArgs(cls, parser):
    worker_pool_presentation = presentation_specs.ResourcePresentationSpec(
        'WORKER_POOL',
        resource_args.GetV2WorkerPoolResourceSpec(prompt=True),
        'WorkerPool to update instance split of.',
        required=True,
        prefixes=False,
    )
    concept_parsers.ConceptParser([worker_pool_presentation]).AddToParser(
        parser
    )
    flags.AddAsyncFlag(parser)
    flags.AddUpdateInstanceSplitFlags(parser)
    flags.AddBinAuthzBreakglassFlag(parser)

    resource_printer.RegisterFormatter(
        instance_split_printer.INSTANCE_SPLIT_PRINTER_FORMAT,
        instance_split_printer.InstanceSplitPrinter,
        hidden=True,
    )
    parser.display_info.AddFormat(
        instance_split_printer.INSTANCE_SPLIT_PRINTER_FORMAT
    )

  @classmethod
  def Args(cls, parser):
    cls.CommonArgs(parser)

  def _GetBaseChanges(self, args):
    """Returns the worker pool config changes with some default settings."""
    changes = flags_parser.GetWorkerPoolConfigurationChanges(
        args, self.ReleaseTrack()
    )
    if not changes:
      raise serverless_exceptions.NoConfigurationChangeError(
          'No instance split configuration change requested.'
      )
    changes.insert(
        0,
        config_changes_mod.BinaryAuthorizationChange(
            breakglass_justification=None
        ),
    )
    changes.append(config_changes_mod.SetLaunchStageChange(self.ReleaseTrack()))
    return changes

  def Run(self, args):
    """Update the instance split for the worker."""
    worker_pool_ref = args.CONCEPTS.worker_pool.Parse()
    flags.ValidateResource(worker_pool_ref)

    def DeriveRegionalEndpoint(endpoint):
      region = args.CONCEPTS.worker_pool.Parse().locationsId
      return region + '-' + endpoint

    run_client = apis.GetGapicClientInstance(
        'run', 'v2', address_override_func=DeriveRegionalEndpoint
    )
    worker_pools_client = worker_pools_operations.WorkerPoolsOperations(
        run_client
    )
    config_changes = self._GetBaseChanges(args)
    with progress_tracker.StagedProgressTracker(
        'Updating instance split...',
        stages.UpdateInstanceSplitStages(),
        failure_message='Updating instance split failed',
        suppress_output=args.async_,
    ):
      response = worker_pools_client.UpdateInstanceSplit(
          worker_pool_ref,
          config_changes,
      )

      if args.async_:
        pretty_print.Success('Updating instance split asynchronously.')
      else:
        response.result()  # Wait for the operation to complete.
        return instance_split.GetInstanceSplitPairs(response.metadata)
