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
"""Command for updating env vars and other configuration info."""

from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import config_changes as config_changes_mod
from googlecloudsdk.command_lib.run import container_parser
from googlecloudsdk.command_lib.run import exceptions
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import messages_util
from googlecloudsdk.command_lib.run import pretty_print
from googlecloudsdk.command_lib.run import resource_args
from googlecloudsdk.command_lib.run import resource_name_conversion
from googlecloudsdk.command_lib.run import stages
from googlecloudsdk.command_lib.run.v2 import config_changes as v2_config_changes_mod
from googlecloudsdk.command_lib.run.v2 import flags_parser
from googlecloudsdk.command_lib.run.v2 import worker_pools_operations
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.command_lib.util.concepts import presentation_specs
from googlecloudsdk.core.console import progress_tracker


def ContainerArgGroup(release_track=base.ReleaseTrack.GA):
  """Returns an argument group with all container update args."""

  help_text = """
Container Flags

  The following flags apply to the container.
"""
  group = base.ArgumentGroup(help=help_text)
  group.AddArgument(flags.ImageArg(required=False))
  group.AddArgument(flags.MutexEnvVarsFlags(release_track=release_track))
  group.AddArgument(flags.MemoryFlag())
  group.AddArgument(flags.CpuFlag())
  group.AddArgument(flags.CommandFlag())
  group.AddArgument(flags.ArgsFlag())
  group.AddArgument(flags_parser.SecretsFlags())
  group.AddArgument(flags.DependsOnFlag())
  group.AddArgument(flags.AddVolumeMountFlag())
  group.AddArgument(flags.RemoveVolumeMountFlag())
  group.AddArgument(flags.ClearVolumeMountsFlag())
  # ALPHA and BETA features
  if (
      release_track == base.ReleaseTrack.ALPHA
      or release_track == base.ReleaseTrack.BETA
  ):
    group.AddArgument(flags.GpuFlag())

  return group


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class Update(base.Command):
  """Update Cloud Run environment variables and other configuration settings."""

  detailed_help = {
      'DESCRIPTION': """\
          {description}
          """,
      'EXAMPLES': """\
          To update one or more env vars:

              $ {command} myworkerpool --update-env-vars=KEY1=VALUE1,KEY2=VALUE2
         """,
  }

  input_flags = (
      '`--update-env-vars`, `--memory`, `--concurrency`, `--timeout`,'
      ' `--connectivity`, `--image`'
  )

  @classmethod
  def CommonArgs(cls, parser):
    flags.AddBinAuthzPolicyFlags(parser)
    flags.AddBinAuthzBreakglassFlag(parser)
    flags_parser.AddCloudSQLFlags(parser)
    flags.AddCmekKeyFlag(parser)
    flags.AddCmekKeyRevocationActionTypeFlag(parser)
    flags.AddDescriptionFlag(parser)
    flags.AddEgressSettingsFlag(parser)
    flags.AddEncryptionKeyShutdownHoursFlag(parser)
    flags.AddRevisionSuffixArg(parser)
    flags.AddRuntimeFlag(parser)
    flags.AddVolumesFlags(parser, cls.ReleaseTrack())
    flags.AddScalingFlag(
        parser, release_track=cls.ReleaseTrack(), resource_kind='worker'
    )
    flags.AddVpcNetworkGroupFlagsForUpdate(parser, resource_kind='worker')
    flags.RemoveContainersFlag().AddToParser(parser)
    flags.AddAsyncFlag(parser)
    flags.AddLabelsFlags(parser)
    flags.AddGeneralAnnotationFlags(parser)
    flags.AddServiceAccountFlag(parser)
    flags.AddClientNameAndVersionFlags(parser)
    flags.AddNoPromoteFlag(parser)
    flags.AddGpuTypeFlag(parser)
    flags.GpuZonalRedundancyFlag(parser)
    worker_pool_presentation = presentation_specs.ResourcePresentationSpec(
        'WORKER_POOL',
        resource_args.GetV2WorkerPoolResourceSpec(prompt=True),
        'WorkerPool to update the configuration of.',
        required=True,
        prefixes=False,
    )
    concept_parsers.ConceptParser([worker_pool_presentation]).AddToParser(
        parser
    )
    # No output by default, can be overridden by --format
    parser.display_info.AddFormat('none')

  @classmethod
  def Args(cls, parser):
    cls.CommonArgs(parser)
    container_args = ContainerArgGroup(cls.ReleaseTrack())
    container_parser.AddContainerFlags(
        parser, container_args, cls.ReleaseTrack()
    )

  def _AssertChanges(self, changes, flags_text, ignore_empty):
    if ignore_empty:
      return
    if not changes or (
        len(changes) == 1
        and isinstance(
            changes[0],
            v2_config_changes_mod.SetClientNameAndVersionChange,
        )
    ):
      raise exceptions.NoConfigurationChangeError(
          'No configuration change requested. '
          'Did you mean to include the flags {}?'.format(flags_text)
      )

  def _GetBaseChanges(self, args, ignore_empty=False):
    """Returns the worker pool config changes with some default settings."""
    changes = flags_parser.GetWorkerPoolConfigurationChanges(
        args, self.ReleaseTrack()
    )
    self._AssertChanges(changes, self.input_flags, ignore_empty)
    changes.insert(
        0,
        v2_config_changes_mod.BinaryAuthorizationChange(
            breakglass_justification=None
        ),
    )
    changes.append(
        v2_config_changes_mod.SetLaunchStageChange(self.ReleaseTrack())
    )
    return changes

  def Run(self, args):
    """Update the worker-pool resource."""
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
    worker_pool = worker_pools_client.GetWorkerPool(worker_pool_ref)
    messages_util.MaybeLogDefaultGpuTypeMessageForV2Resource(args, worker_pool)
    config_changes = self._GetBaseChanges(args)
    if worker_pool:
      header = 'Updating...'
      failure_message = 'Update failed'
      result_message = 'updating'
    else:
      header = 'Deploying new worker pool...'
      failure_message = 'Deployment failed'
      result_message = 'deploying'
    creates_revision = config_changes_mod.AdjustsTemplate(config_changes)
    with progress_tracker.StagedProgressTracker(
        header,
        stages.WorkerPoolStages(include_create_revision=creates_revision),
        failure_message=failure_message,
        suppress_output=args.async_,
    ):
      # TODO: b/432102851 - Add retry logic with zonal redundancy off.
      response = worker_pools_client.ReleaseWorkerPool(
          worker_pool_ref, config_changes, prefetch=worker_pool
      )
      if not response:
        raise exceptions.ArgumentError(
            'Cannot update worker pool [{}]'.format(
                worker_pool_ref.workerPoolsId
            )
        )

      if args.async_:
        pretty_print.Success(
            'Worker pool [{{bold}}{worker_pool}{{reset}}] is {result_message} '
            'asynchronously.'.format(
                worker_pool=worker_pool_ref.workerPoolsId,
                result_message=result_message,
            )
        )
      else:
        response.result()  # Wait for the operation to complete.
        msg = 'Worker pool [{{bold}}{worker_pool}{{reset}}]'.format(
            worker_pool=worker_pool_ref.workerPoolsId
        )
        if response.metadata and response.metadata.latest_created_revision:
          rev = resource_name_conversion.GetNameFromFullChildName(
              response.metadata.latest_created_revision
          )
          msg += ' revision [{{bold}}{rev}{{reset}}]'.format(rev=rev)
        if worker_pool and not creates_revision:
          pretty_print.Success(msg + ' has been updated.')
        else:
          pretty_print.Success(msg + ' has been deployed.')


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AlphaUpdate(Update):
  """Update a Cloud Run worker-pool."""

  @classmethod
  def Args(cls, parser):
    cls.CommonArgs(parser)
    flags.AddWorkerPoolMinInstancesFlag(parser)
    flags.AddWorkerPoolMaxInstancesFlag(parser)
    container_args = ContainerArgGroup(cls.ReleaseTrack())
    container_parser.AddContainerFlags(
        parser, container_args, cls.ReleaseTrack()
    )


AlphaUpdate.__doc__ = Update.__doc__
