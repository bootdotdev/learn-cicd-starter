# -*- coding: utf-8 -*- #
# Copyright 2021 Google LLC. All Rights Reserved.
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
"""Create a release."""


import datetime
import os.path

from googlecloudsdk.api_lib.clouddeploy import client_util
from googlecloudsdk.api_lib.clouddeploy import release
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exceptions
from googlecloudsdk.command_lib.deploy import delivery_pipeline_util
from googlecloudsdk.command_lib.deploy import deploy_policy_util
from googlecloudsdk.command_lib.deploy import deploy_util
from googlecloudsdk.command_lib.deploy import flags
from googlecloudsdk.command_lib.deploy import promote_util
from googlecloudsdk.command_lib.deploy import release_util
from googlecloudsdk.command_lib.deploy import resource_args
from googlecloudsdk.core import exceptions as core_exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import resources
from googlecloudsdk.core.util import files
from googlecloudsdk.core.util import times


_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
    To create a release with source located at storage URL `gs://bucket/object.zip`
    and the first rollout in the first target of the promotion sequence:

       $ {command} my-release --source=`gs://bucket/object.zip` --delivery-pipeline=my-pipeline --region=us-central1

    To create a release with source located at current directory
    and deploy a rollout to target prod :

      $ {command} my-release --delivery-pipeline=my-pipeline --region=us-central1 --to-target=prod

    The following command creates a release without a `skaffold.yaml` as input, and generates one
    for you:

      $ {command} my-release --delivery-pipeline=my-pipeline --region=us-central1 --from-k8s-manifest=path/to/kubernetes/k8.yaml

    The current UTC date and time on the machine running the gcloud command can
    also be included in the release name by adding $DATE and $TIME parameters:

      $ {command} 'my-release-$DATE-$TIME' --delivery-pipeline=my-pipeline --region=us-central1

    If the current UTC date and time is set to 2021-12-21 12:02, then the created release
    will have its name set as my-release-20211221-1202.

    When using these parameters, please be sure to wrap the release name in single quotes
    or else the template parameters will be overridden by environment variables.
    """,
}
_RELEASE = 'release'
_MAINTENANCE_WARNING_DAYS = 28


def _CommonArgs(parser):
  """Register flags for this command.

  Args:
    parser: An argparse.ArgumentParser-like object. It is mocked out in order to
      capture some information, but behaves like an ArgumentParser.
  """
  resource_args.AddReleaseResourceArg(parser, positional=True, required=True)
  flags.AddGcsSourceStagingDirFlag(parser)
  flags.AddImagesGroup(parser)
  flags.AddIgnoreFileFlag(parser)
  flags.AddToTargetFlag(parser)
  flags.AddDescription(parser, 'Description of the release.')
  flags.AddAnnotationsFlag(parser, _RELEASE)
  flags.AddLabelsFlag(parser, _RELEASE)
  flags.AddDockerVersion(parser)
  flags.AddHelmVersion(parser)
  flags.AddKptVersion(parser)
  flags.AddKubectlVersion(parser)
  flags.AddKustomizeVersion(parser)
  flags.AddSkaffoldVersion(parser)
  flags.AddConfigSourcesGroup(parser)
  flags.AddInitialRolloutGroup(parser)
  flags.AddDeployParametersFlag(parser)
  flags.AddOverrideDeployPolicies(parser)


@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
@base.DefaultUniverseOnly
class Create(base.CreateCommand):
  """Creates a new release, delivery pipeline qualified."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    _CommonArgs(parser)

  def _CheckIfNearMaintenance(self, release_obj):
    """Checks to see if a release is close to the maintenance window."""

    def _ParseDt(dt):
      """Parses the maintenance dt, returning a datetime or None."""
      if dt is None:
        return None
      try:
        return times.ParseDateTime(dt)
      except (times.DateTimeSyntaxError, times.DateTimeValueError):
        return None

    release_condition = release_obj.condition
    if release_condition is None:
      return

    has_tool_versions = (
        release_condition.dockerVersionSupportedCondition
        or release_condition.helmVersionSupportedCondition
        or release_condition.kptVersionSupportedCondition
        or release_condition.kubectlVersionSupportedCondition
        or release_condition.kustomizeVersionSupportedCondition
        or release_condition.skaffoldVersionSupportedCondition
    )
    if not has_tool_versions:
      if release_condition.skaffoldSupportedCondition is None:
        return
      maintenance_dt = _ParseDt(
          release_condition.skaffoldSupportedCondition.maintenanceModeTime
      )
      # It is possible to have no maintenance mode time.
      # Like `skaffold_preview` for example.
      if (
          maintenance_dt is not None
          and maintenance_dt - times.Now()
          <= datetime.timedelta(days=_MAINTENANCE_WARNING_DAYS)
      ):
        log.status.Print(
            "WARNING: This release's Skaffold version will be"
            ' in maintenance mode beginning on {date}.'
            " After that you won't be able to create releases"
            ' using this version of Skaffold.\n'
            'https://cloud.google.com/deploy/docs/using-skaffold'
            '/select-skaffold#skaffold_version_deprecation'
            '_and_maintenance_policy'.format(
                date=maintenance_dt.strftime('%Y-%m-%d')
            )
        )
      return

    # use an array to have deterministic ordering.
    tools_supported_condition_to_process = [
        (
            release_util.Tools.DOCKER,
            release_condition.dockerVersionSupportedCondition,
        ),
        (
            release_util.Tools.HELM,
            release_condition.helmVersionSupportedCondition,
        ),
        (
            release_util.Tools.KPT,
            release_condition.kptVersionSupportedCondition,
        ),
        (
            release_util.Tools.KUBECTL,
            release_condition.kubectlVersionSupportedCondition,
        ),
        (
            release_util.Tools.KUSTOMIZE,
            release_condition.kustomizeVersionSupportedCondition,
        ),
        (
            release_util.Tools.SKAFFOLD,
            release_condition.skaffoldVersionSupportedCondition,
        ),
    ]
    tools_almost_in_maintenance = []
    for tool, condition in tools_supported_condition_to_process:
      if not condition:
        continue
      maintenance_dt = _ParseDt(condition.maintenanceModeTime)
      if (
          maintenance_dt is not None
          and maintenance_dt - times.Now()
          <= datetime.timedelta(days=_MAINTENANCE_WARNING_DAYS)
      ):
        tools_almost_in_maintenance.append(tool)
    if tools_almost_in_maintenance:
      joined = ', '.join([tool.value for tool in tools_almost_in_maintenance])
      log.status.Print(
          f'WARNING: The versions used for tools: [{joined}] will be in'
          " maintenance mode soon. After that you won't be able to create"
          ' releases using these versions of the tools.\n'
          'https://cloud.google.com/deploy/docs/select-tool-version'
      )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: All the arguments that were provided to this command invocation.

    Returns:
      The release and rollout created.
    """
    if args.disable_initial_rollout and args.to_target:
      raise c_exceptions.ConflictingArgumentsException(
          '--disable-initial-rollout', '--to-target'
      )

    args.CONCEPTS.parsed_args.release = release_util.RenderPattern(
        args.CONCEPTS.parsed_args.release
    )
    release_ref = args.CONCEPTS.release.Parse()
    pipeline_obj = delivery_pipeline_util.GetPipeline(
        release_ref.Parent().RelativeName()
    )
    failed_activity_msg = 'Cannot create release {}.'.format(
        release_ref.RelativeName()
    )
    delivery_pipeline_util.ThrowIfPipelineSuspended(
        pipeline_obj, failed_activity_msg
    )

    # Only when the skaffold file is an absolute path needs to be handled
    # here.
    if args.skaffold_file and os.path.isabs(args.skaffold_file):
      if args.source == '.':
        source = os.getcwd()
        source_description = 'current working directory'
      else:
        source = args.source
        source_description = 'source'
      if not files.IsDirAncestorOf(source, args.skaffold_file):
        raise core_exceptions.Error(
            'The skaffold file {} could not be found in the {}. Please enter'
            ' a valid Skaffold file path.'.format(
                args.skaffold_file, source_description
            )
        )
      args.skaffold_file = os.path.relpath(
          os.path.abspath(args.skaffold_file), os.path.abspath(source)
      )

    # Only when the deploy config is an absolute path needs to be handled
    # here.
    if args.deploy_config_file and os.path.isabs(args.deploy_config_file):
      if args.source == '.':
        source = os.getcwd()
        source_description = 'current working directory'
      else:
        source = args.source
        source_description = 'source'
      if not files.IsDirAncestorOf(source, args.deploy_config_file):
        raise core_exceptions.Error(
            'The deploy config file {} could not be found in the {}. Please'
            ' enter a valid deploy config file path.'.format(
                args.deploy_config_file, source_description
            )
        )
      args.deploy_config_file = os.path.relpath(
          os.path.abspath(args.deploy_config_file), os.path.abspath(source)
      )

    client = release.ReleaseClient()
    # Create the release create request.
    release_config = release_util.CreateReleaseConfig(
        args.source,
        args.gcs_source_staging_dir,
        args.ignore_file,
        args.images,
        args.build_artifacts,
        args.description,
        args.docker_version,
        args.helm_version,
        args.kpt_version,
        args.kubectl_version,
        args.kustomize_version,
        args.skaffold_version,
        args.skaffold_file,
        args.deploy_config_file,
        release_ref.AsDict()['locationsId'],
        pipeline_obj.uid,
        args.from_k8s_manifest,
        args.from_run_manifest,
        pipeline_obj,
        args.deploy_parameters,
    )

    deploy_util.SetMetadata(
        client.messages,
        release_config,
        deploy_util.ResourceType.RELEASE,
        args.annotations,
        args.labels,
    )
    operation = client.Create(release_ref, release_config)
    operation_ref = resources.REGISTRY.ParseRelativeName(
        operation.name, collection='clouddeploy.projects.locations.operations'
    )
    client_util.OperationsClient().WaitForOperation(operation, operation_ref)

    log.status.Print(
        'Created Cloud Deploy release {}.'.format(release_ref.Name())
    )

    release_obj = release.ReleaseClient().Get(release_ref.RelativeName())
    self._CheckIfNearMaintenance(release_obj)
    if args.disable_initial_rollout:
      return release_obj
    # On the command line deploy policy IDs are provided, but for the
    # CreateRollout API we need to provide the full resource name.
    pipeline_ref = release_ref.Parent()
    policies = deploy_policy_util.CreateDeployPolicyNamesFromIDs(
        pipeline_ref, args.override_deploy_policies
    )
    rollout_resource = promote_util.Promote(
        release_ref,
        release_obj,
        args.to_target,
        is_create=True,
        labels=args.initial_rollout_labels,
        annotations=args.initial_rollout_annotations,
        starting_phase_id=args.initial_rollout_phase_id,
        override_deploy_policies=policies,
    )

    return release_obj, rollout_resource
