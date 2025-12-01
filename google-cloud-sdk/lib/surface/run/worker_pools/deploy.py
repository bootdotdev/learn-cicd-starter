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
"""Deploy a container to Cloud Run that will handle workloads that are not ingress based."""

import enum
import os.path

from googlecloudsdk.api_lib.run import api_enabler
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exceptions
from googlecloudsdk.command_lib.artifacts import docker_util
from googlecloudsdk.command_lib.run import artifact_registry
from googlecloudsdk.command_lib.run import connection_context
from googlecloudsdk.command_lib.run import container_parser
from googlecloudsdk.command_lib.run import exceptions
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import messages_util
from googlecloudsdk.command_lib.run import pretty_print
from googlecloudsdk.command_lib.run import resource_args
from googlecloudsdk.command_lib.run import resource_name_conversion
from googlecloudsdk.command_lib.run import stages
from googlecloudsdk.command_lib.run.v2 import config_changes as config_changes_mod
from googlecloudsdk.command_lib.run.v2 import flags_parser
from googlecloudsdk.command_lib.run.v2 import worker_pools_operations
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.command_lib.util.concepts import presentation_specs
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io
from googlecloudsdk.core.console import progress_tracker


class BuildType(enum.Enum):
  DOCKERFILE = 'Dockerfile'
  BUILDPACKS = 'Buildpacks'


def ContainerArgGroup(release_track=base.ReleaseTrack.GA):
  """Returns an argument group with all container deploy args."""

  help_text = """
Container Flags

  The following flags apply to the container.
"""
  group = base.ArgumentGroup(help=help_text)
  group.AddArgument(flags.SourceAndImageFlags())
  group.AddArgument(flags.MutexEnvVarsFlags(release_track=release_track))
  group.AddArgument(flags.MemoryFlag())
  group.AddArgument(flags.CpuFlag())
  group.AddArgument(flags.ArgsFlag())
  group.AddArgument(flags_parser.SecretsFlags())
  group.AddArgument(flags.DependsOnFlag())
  group.AddArgument(flags.CommandFlag())
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
class Deploy(base.Command):
  """Create or update a Cloud Run worker-pool."""

  detailed_help = {
      'DESCRIPTION': """\
          Creates or updates a Cloud Run worker-pool.
          """,
      'EXAMPLES': """\
          To deploy a container to the worker-pool `my-backend` on Cloud Run:

              $ {command} my-backend --image=us-docker.pkg.dev/project/image

          You may also omit the worker-pool name. Then a prompt will be displayed
          with a suggested default value:

              $ {command} --image=us-docker.pkg.dev/project/image
          """,
  }

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
        'WorkerPool to deploy to.',
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

  def _GetBaseChanges(self, args):
    """Returns the worker pool config changes with some default settings."""
    changes = flags_parser.GetWorkerPoolConfigurationChanges(
        args, self.ReleaseTrack()
    )
    changes.insert(
        0,
        config_changes_mod.BinaryAuthorizationChange(
            breakglass_justification=None
        ),
    )
    changes.append(config_changes_mod.SetLaunchStageChange(self.ReleaseTrack()))
    return changes

  def _ValidateAndGetContainers(self, args):
    if flags.FlagIsExplicitlySet(args, 'containers'):
      containers = args.containers
    else:
      containers = {'': args}

    if len(containers) > 10:
      raise c_exceptions.InvalidArgumentException(
          '--container', 'Worker pools may include at most 10 containers'
      )
    return containers

  def _ValidateAndGetBuildFromSource(self, containers):
    build_from_source = {
        name: container
        for name, container in containers.items()
        if (
            not container.IsSpecified('image')
            or flags.FlagIsExplicitlySet(container, 'source')
        )
    }
    if len(build_from_source) > 1:
      needs_image = [
          name
          for name, container in build_from_source.items()
          if not flags.FlagIsExplicitlySet(container, 'source')
      ]
      if needs_image:
        raise exceptions.RequiredImageArgumentException(needs_image)
      raise c_exceptions.InvalidArgumentException(
          '--container', 'At most one container can be deployed from source.'
      )
    for name, container in build_from_source.items():
      if not flags.FlagIsExplicitlySet(container, 'source'):
        if console_io.CanPrompt():
          container.source = flags.PromptForDefaultSource(name)
        else:
          if name:
            message = (
                'Container {} requires a container image to deploy (e.g.'
                ' `gcr.io/cloudrun/hello:latest`) if no build source is'
                ' provided.'.format(name)
            )
          else:
            message = (
                'Requires a container image to deploy (e.g.'
                ' `gcr.io/cloudrun/hello:latest`) if no build source is'
                ' provided.'
            )
          raise c_exceptions.RequiredArgumentException(
              '--image',
              message,
          )
    return build_from_source

  def _GetRequiredApis(self):
    return [api_enabler.get_run_api()]

  def _BuildFromSource(
      self,
      args,
      build_from_source,
      already_activated_services,
      worker_pool_ref,
  ):
    # Only one container can deployed from source
    name, container_args = next(iter(build_from_source.items()))
    pack = None
    build_type = None
    repo_to_create = None
    source = container_args.source

    ar_repo = docker_util.DockerRepo(
        project_id=properties.VALUES.core.project.Get(required=True),
        location_id=artifact_registry.RepoRegion(args),
        repo_id='cloud-run-source-deploy',
    )
    if artifact_registry.ShouldCreateRepository(
        ar_repo, skip_activation_prompt=already_activated_services
    ):
      repo_to_create = ar_repo
    # The image is built with latest tag. After build, the image digest
    # from the build result will be added to the image of the worker pool spec.
    container_args.image = '{repo}/{worker_pool}'.format(
        repo=ar_repo.GetDockerString(),
        worker_pool=worker_pool_ref.workerPoolsId,
    )
    docker_file = source + '/Dockerfile'
    if os.path.exists(docker_file):
      build_type = BuildType.DOCKERFILE
    else:
      pack = _CreateBuildPack(container_args, self.ReleaseTrack())
      build_type = BuildType.BUILDPACKS
    image = None if pack else container_args.image

    operation_message = (
        'Building using {build_type} and deploying container to'
    ).format(build_type=build_type.value)

    return (
        image,
        pack,
        source,
        operation_message,
        repo_to_create,
        name,
    )

  def Run(self, args):
    """Deploy a WorkerPool container to Cloud Run."""
    containers = self._ValidateAndGetContainers(args)
    build_from_source = self._ValidateAndGetBuildFromSource(containers)

    worker_pool_ref = args.CONCEPTS.worker_pool.Parse()
    flags.ValidateResource(worker_pool_ref)

    required_apis = self._GetRequiredApis()
    if build_from_source:
      required_apis.append('artifactregistry.googleapis.com')
      required_apis.append('cloudbuild.googleapis.com')
    already_activated_services = api_enabler.check_and_enable_apis(
        properties.VALUES.core.project.Get(), required_apis
    )
    # Obtaining the connection context prompts the user to select a region if
    # one hasn't been provided. We want to do this prior to preparing a source
    # deploy so that we can use that region for the Artifact Registry repo.
    conn_context = connection_context.GetConnectionContext(
        args,
        flags.Product.RUN,
        self.ReleaseTrack(),
    )

    def DeriveRegionalEndpoint(endpoint):
      region = args.CONCEPTS.worker_pool.Parse().locationsId
      return region + '-' + endpoint

    run_client = apis.GetGapicClientInstance(
        'run', 'v2', address_override_func=DeriveRegionalEndpoint
    )
    worker_pools_client = worker_pools_operations.WorkerPoolsOperations(
        run_client
    )
    # pre-fetch the worker pool in case it already exists.
    worker_pool = worker_pools_client.GetWorkerPool(worker_pool_ref)
    messages_util.MaybeLogDefaultGpuTypeMessageForV2Resource(args, worker_pool)

    build_image = None
    build_pack = None
    build_source = None
    operation_message = 'Deploying container to'
    repo_to_create = None
    # Name of the container to be deployed from source.
    container_name = None
    if build_from_source:
      (
          build_image,
          build_pack,
          build_source,
          operation_message,
          repo_to_create,
          container_name,
      ) = self._BuildFromSource(
          args, build_from_source, already_activated_services, worker_pool_ref
      )
    pretty_print.Info(
        messages_util.GetStartDeployMessage(
            conn_context,
            worker_pool_ref,
            operation_message,
            resource_kind_lower='worker pool',
        )
    )
    config_changes = self._GetBaseChanges(args)
    header = 'Deploying'
    if worker_pool is None:
      header += ' new worker pool'
    header += '...'
    with progress_tracker.StagedProgressTracker(
        header,
        stages.WorkerPoolStages(
            include_build=bool(build_from_source),
            include_create_repo=repo_to_create is not None,
        ),
        failure_message='Deployment failed',
        suppress_output=args.async_,
    ) as tracker:
      # TODO: b/432102851 - Add retry logic with zonal redundancy off.
      response = worker_pools_client.ReleaseWorkerPool(
          worker_pool_ref,
          config_changes,
          self.ReleaseTrack(),
          tracker=tracker,
          prefetch=worker_pool,
          build_image=build_image,
          build_pack=build_pack,
          build_source=build_source,
          build_from_source_container_name=container_name,
          repo_to_create=repo_to_create,
          already_activated_services=already_activated_services,
          force_new_revision=True,
      )
      if not response:
        raise exceptions.ArgumentError(
            'Cannot deploy worker pool [{}]'.format(
                worker_pool_ref.workerPoolsId
            )
        )

    if args.async_:
      pretty_print.Success(
          'Worker pool [{{bold}}{worker_pool}{{reset}}] is being deployed '
          'asynchronously.'.format(worker_pool=worker_pool_ref.workerPoolsId)
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
      pretty_print.Success(msg + ' has been deployed.')


def _CreateBuildPack(container, release_track=base.ReleaseTrack.GA):
  """A helper method to cofigure buildpack."""
  pack = [{'image': container.image}]
  if release_track != base.ReleaseTrack.GA:
    command_arg = getattr(container, 'command', None)
    if command_arg is not None:
      command = ' '.join(command_arg)
      pack[0].update(
          {'envs': ['GOOGLE_ENTRYPOINT="{command}"'.format(command=command)]}
      )
  return pack


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AlphaDeploy(Deploy):
  """Create or update a Cloud Run worker-pool."""

  @classmethod
  def Args(cls, parser):
    cls.CommonArgs(parser)
    flags.AddWorkerPoolMinInstancesFlag(parser)
    flags.AddWorkerPoolMaxInstancesFlag(parser)
    container_args = ContainerArgGroup(cls.ReleaseTrack())
    container_parser.AddContainerFlags(
        parser, container_args, cls.ReleaseTrack()
    )


AlphaDeploy.__doc__ = Deploy.__doc__
