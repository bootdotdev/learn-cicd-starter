# -*- coding: utf-8 -*- #
# Copyright 2018 Google LLC. All Rights Reserved.
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

from googlecloudsdk.api_lib.run import k8s_object
from googlecloudsdk.api_lib.run import traffic
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import config_changes
from googlecloudsdk.command_lib.run import connection_context
from googlecloudsdk.command_lib.run import container_parser
from googlecloudsdk.command_lib.run import exceptions
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import messages_util
from googlecloudsdk.command_lib.run import pretty_print
from googlecloudsdk.command_lib.run import resource_args
from googlecloudsdk.command_lib.run import resource_change_validators
from googlecloudsdk.command_lib.run import serverless_operations
from googlecloudsdk.command_lib.run import stages
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.command_lib.util.concepts import presentation_specs
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import progress_tracker


@base.UniverseCompatible
def ContainerArgGroup(release_track=base.ReleaseTrack.GA):
  """Returns an argument group with all per-container update args."""

  help_text = """
Container Flags

    If the --container or --remove-containers flag is specified the following
    arguments may only be specified after a --container flag.
    """
  group = base.ArgumentGroup(help=help_text)
  group.AddArgument(flags.ImageArg(required=False))
  group.AddArgument(flags.PortArg())
  group.AddArgument(flags.Http2Flag())
  group.AddArgument(flags.MutexEnvVarsFlags(release_track=release_track))
  group.AddArgument(flags.MemoryFlag())
  group.AddArgument(flags.CpuFlag())
  group.AddArgument(flags.CommandFlag())
  group.AddArgument(flags.ArgsFlag())
  group.AddArgument(flags.SecretsFlags())
  group.AddArgument(flags.DependsOnFlag())

  group.AddArgument(flags.AddVolumeMountFlag())
  group.AddArgument(flags.RemoveVolumeMountFlag())
  group.AddArgument(flags.ClearVolumeMountsFlag())
  group.AddArgument(flags.StartupProbeFlag())
  group.AddArgument(flags.LivenessProbeFlag())
  group.AddArgument(flags.GpuFlag())

  return group


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Update(base.Command):
  """Update Cloud Run environment variables and other configuration settings."""

  detailed_help = {
      'DESCRIPTION': """\
          {description}
          """,
      'EXAMPLES': """\
          To update one or more env vars:

              $ {command} myservice --update-env-vars=KEY1=VALUE1,KEY2=VALUE2
         """,
  }

  input_flags = (
      '`--update-env-vars`, `--memory`, `--concurrency`, `--timeout`,'
      ' `--connectivity`, `--image`'
  )

  @classmethod
  def CommonArgs(cls, parser):
    # Flags specific to managed CR
    flags.AddBinAuthzPolicyFlags(parser)
    flags.AddBinAuthzBreakglassFlag(parser)
    flags.AddCloudSQLFlags(parser)
    flags.AddCmekKeyFlag(parser)
    flags.AddCmekKeyRevocationActionTypeFlag(parser)
    flags.AddCpuThrottlingFlag(parser)
    flags.AddCustomAudiencesFlag(parser)
    flags.AddDefaultUrlFlag(parser)
    flags.AddDeployHealthCheckFlag(parser)
    flags.AddEgressSettingsFlag(parser)
    flags.AddEncryptionKeyShutdownHoursFlag(parser)
    flags.AddGpuTypeFlag(parser)
    flags.GpuZonalRedundancyFlag(parser)
    flags.AddRevisionSuffixArg(parser)
    flags.AddSandboxArg(parser)
    flags.AddSessionAffinityFlag(parser)
    flags.AddStartupCpuBoostFlag(parser)
    flags.AddVpcConnectorArgs(parser)
    flags.AddVpcNetworkGroupFlagsForUpdate(parser)
    flags.RemoveContainersFlag().AddToParser(parser)
    flags.AddVolumesFlags(parser, cls.ReleaseTrack())
    flags.AddServiceMinMaxInstancesFlag(parser)
    flags.AddInvokerIamCheckFlag(parser)
    flags.AddScalingFlag(parser)
    # Flags specific to connecting to a cluster
    flags.AddEndpointVisibilityEnum(parser)
    flags.CONFIG_MAP_FLAGS.AddToParser(parser)

    # Flags not specific to any platform
    service_presentation = presentation_specs.ResourcePresentationSpec(
        'SERVICE',
        resource_args.GetServiceResourceSpec(prompt=True),
        'Service to update the configuration of.',
        required=True,
        prefixes=False,
    )
    flags.AddConcurrencyFlag(parser)
    flags.AddTimeoutFlag(parser)
    flags.AddAsyncFlag(parser)
    flags.AddLabelsFlags(parser)
    flags.AddGeneralAnnotationFlags(parser)
    flags.AddMinInstancesFlag(parser)
    flags.AddMaxInstancesFlag(parser)
    flags.AddNoTrafficFlag(parser)
    flags.AddDeployTagFlag(parser)
    flags.AddServiceAccountFlag(parser)
    flags.AddClientNameAndVersionFlags(parser)
    flags.AddIngressFlag(parser)
    concept_parsers.ConceptParser([service_presentation]).AddToParser(parser)
    # No output by default, can be overridden by --format
    parser.display_info.AddFormat('none')

  @classmethod
  def Args(cls, parser):
    Update.CommonArgs(parser)
    container_args = ContainerArgGroup(cls.ReleaseTrack())
    container_parser.AddContainerFlags(
        parser, container_args, cls.ReleaseTrack()
    )

  def _ConnectionContext(self, args):
    return connection_context.GetConnectionContext(
        args, flags.Product.RUN, self.ReleaseTrack()
    )

  def _AssertChanges(self, changes, flags_text, ignore_empty):
    if ignore_empty:
      return
    if not changes or (
        len(changes) == 1
        and isinstance(
            changes[0],
            config_changes.SetClientNameAndVersionAnnotationChange,
        )
    ):
      raise exceptions.NoConfigurationChangeError(
          'No configuration change requested. '
          'Did you mean to include the flags {}?'.format(flags_text)
      )

  def _GetBaseChanges(self, args, existing_service=None, ignore_empty=False):  # pylint: disable=unused-argument
    changes = flags.GetServiceConfigurationChanges(args, self.ReleaseTrack())
    self._AssertChanges(changes, self.input_flags, ignore_empty)
    changes.insert(
        0,
        config_changes.DeleteAnnotationChange(
            k8s_object.BINAUTHZ_BREAKGLASS_ANNOTATION
        ),
    )
    changes.append(
        config_changes.SetLaunchStageAnnotationChange(self.ReleaseTrack())
    )
    return changes

  def _IsMultiRegion(self):
    return False

  def _GetMultiRegionRegions(self, changes, service):  # used by child - pylint: disable=unused-argument
    return None

  def _GetIap(self, args):
    if flags.FlagIsExplicitlySet(args, 'iap'):
      return args.iap
    return None

  def Run(self, args):
    """Update the service resource.

       Different from `deploy` in that it can only update the service spec but
       no IAM or Cloud build changes.

    Args:
      args: Args!

    Returns:
      googlecloudsdk.api_lib.run.Service, the updated service
    """

    conn_context = self._ConnectionContext(args)
    service_ref = args.CONCEPTS.service.Parse()
    flags.ValidateResource(service_ref)
    iap = self._GetIap(args)
    with serverless_operations.Connect(conn_context) as client:
      service = client.GetService(service_ref)
      messages_util.MaybeLogDefaultGpuTypeMessage(args, service)
      changes = self._GetBaseChanges(args, service)
      resource_change_validators.ValidateClearVpcConnector(service, args)
      has_latest = (
          service is None or traffic.LATEST_REVISION_KEY in service.spec_traffic
      )
      creates_revision = config_changes.AdjustsTemplate(changes)
      multiregion_regions = self._GetMultiRegionRegions(changes, service)
      deployment_stages = stages.ServiceStages(
          include_iam_policy_set=False,
          include_route=creates_revision and has_latest,
          include_create_revision=creates_revision,
          regions_list=multiregion_regions,
          include_iap=iap is not None,
      )
      if creates_revision:
        progress_message = 'Deploying...'
        failure_message = 'Deployment failed'
        result_message = 'deploying'
      else:
        progress_message = 'Updating...'
        failure_message = 'Update failed'
        result_message = 'updating'

      def _ReleaseService(changes_):
        with progress_tracker.StagedProgressTracker(
            progress_message,
            deployment_stages,
            failure_message=failure_message,
            suppress_output=args.async_,
        ) as tracker:
          return client.ReleaseService(
              service_ref,
              changes_,
              self.ReleaseTrack(),
              tracker,
              asyn=args.async_,
              prefetch=service,
              generate_name=(
                  flags.FlagIsExplicitlySet(args, 'revision_suffix')
                  or flags.FlagIsExplicitlySet(args, 'tag')
              ),
              is_verbose=properties.VALUES.core.verbosity.Get() == 'debug',
              iap_enabled=iap,
              multiregion_regions=multiregion_regions,
          )

      try:
        service = _ReleaseService(changes)
      except exceptions.HttpError as e:
        if flags.ShouldRetryNoZonalRedundancy(args, str(e)):
          changes.append(
              config_changes.GpuZonalRedundancyChange(
                  gpu_zonal_redundancy=False
              )
          )
          service = _ReleaseService(changes)
        else:
          raise e

      if args.async_:
        pretty_print.Success(
            'Service [{{bold}}{serv}{{reset}}] is {result_message} '
            'asynchronously.'.format(
                serv=service.name, result_message=result_message
            )
        )
      else:
        if creates_revision:
          pretty_print.Success(
              messages_util.GetSuccessMessageForSynchronousDeploy(
                  service, args.no_traffic
              )
          )
        else:
          pretty_print.Success(
              'Service [{{bold}}{serv}{{reset}}] has been updated.'.format(
                  serv=service.name
              )
          )
      return service


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class BetaUpdate(Update):
  """Update Cloud Run environment variables and other configuration settings."""

  input_flags = (
      '`--update-env-vars`, `--memory`, `--concurrency`, `--timeout`,'
      ' `--connectivity`, `--image`, `--iap`'
  )

  @classmethod
  def Args(cls, parser):
    cls.CommonArgs(parser)

    # Flags specific to managed CR
    flags.SERVICE_MESH_FLAG.AddToParser(parser)
    flags.AddIapFlag(parser)
    container_args = ContainerArgGroup(cls.ReleaseTrack())
    container_parser.AddContainerFlags(
        parser, container_args, cls.ReleaseTrack()
    )


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AlphaUpdate(BetaUpdate):
  """Update Cloud Run environment variables and other configuration settings."""

  input_flags = (
      '`--update-env-vars`, `--memory`, `--concurrency`, `--timeout`,'
      ' `--connectivity`, `--image`, `--iap`'
  )

  @classmethod
  def Args(cls, parser):
    cls.CommonArgs(parser)

    # Flags specific to managed CR
    flags.AddIapFlag(parser)
    flags.AddRuntimeFlag(parser)
    flags.AddDescriptionFlag(parser)
    flags.SERVICE_MESH_FLAG.AddToParser(parser)
    flags.IDENTITY_FLAG.AddToParser(parser)
    flags.ENABLE_WORKLOAD_CERTIFICATE_FLAG.AddToParser(parser)
    flags.MESH_DATAPLANE_FLAG.AddToParser(parser)
    flags.AddOverflowScalingFlag(parser)
    flags.AddCpuUtilizationFlag(parser)
    flags.AddConcurrencyUtilizationFlag(parser)
    flags.AddClearPresetFlag(parser)
    container_args = ContainerArgGroup(cls.ReleaseTrack())
    container_args.AddArgument(flags.ReadinessProbeFlag())
    container_parser.AddContainerFlags(
        parser, container_args, cls.ReleaseTrack()
    )


AlphaUpdate.__doc__ = Update.__doc__
