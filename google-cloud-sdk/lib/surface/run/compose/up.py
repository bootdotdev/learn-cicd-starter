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
"""Command for deploying containers from Compose file to Cloud Run."""

import os

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.artifacts import docker_util
from googlecloudsdk.command_lib.projects import util as projects_util
from googlecloudsdk.command_lib.run import artifact_registry
from googlecloudsdk.command_lib.run import exceptions
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import pretty_print
from googlecloudsdk.command_lib.run import up
from googlecloudsdk.command_lib.run.compose import compose_resource
from googlecloudsdk.command_lib.run.compose import tracker as stages
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import progress_tracker


DEFAULT_REPO_NAME = 'cloud-run-source-deploy'


@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Up(base.BinaryBackedCommand):
  """Deploy to Cloud Run from compose specification."""

  detailed_help = {
      'DESCRIPTION': """\
          {description}
          """,
      'EXAMPLES': """\
          To deploy a container from the source Compose file on Cloud Run:

              $ {command} compose.yaml

          To deploy to Cloud Run with unauthenticated access:

              $ {command} compose.yaml --allow-unauthenticated
         """,
  }

  @staticmethod
  def CommonArgs(parser):
    flags.AddDeployFromComposeArgument(parser)
    flags.AddRegionArg(parser)
    flags.AddDebugFlag(parser)
    flags.AddDryRunFlag(parser)
    flags.AddAllowUnauthenticatedFlag(parser)
    parser.add_argument(
        '--no-build',
        action='store_true',
        help='Skip building from source if applicable.',
    )

  @staticmethod
  def Args(parser):
    Up.CommonArgs(parser)

  def _ResourceAndTranslateRun(
      self, command_executor, compose_file, repo, project_number, region, args
  ):
    """Handles the resource and translate run logic."""
    release_track = self.ReleaseTrack()
    resource_response = command_executor(
        command='resource',
        compose_file=compose_file,
        debug=args.debug,
        dry_run=args.dry_run,
        region=region,
    )
    if not resource_response.stdout:
      # This should never happen since project is always returned by resource
      # command
      log.error(
          f'Resource command failed with error: {resource_response.stderr}'
      )
      raise exceptions.ConfigurationError(
          'No resource config found in compose file.'
      )
    try:
      config = compose_resource.ResourcesConfig.from_json(
          resource_response.stdout[0]
      )
      log.debug('Successfully parsed resources config proto.')
      log.debug(f'ResourcesConfig:\n{config}')
      with progress_tracker.StagedProgressTracker(
          'Setting up resources...',
          self._AddTrackerStages(config),
          failure_message='Setup failed',
          suppress_output=False,
          success_message='Resource setup complete.',
      ) as tracker:
        resources_config = config.handle_resources(
            region, repo, tracker, args.no_build
        )
        log.debug(f'Handled ResourcesConfig:\n{resources_config}')

      # Serialize the handled config to JSON
      resources_config_json = resources_config.to_json()
      response = command_executor(
          command='translate',
          repo=repo,
          compose_file=compose_file,
          resources_config=resources_config_json,  # Pass the JSON string
          debug=args.debug,
          dry_run=args.dry_run,
          project_number=project_number,
          region=region,
      )

      if response.stdout:
        translate_result = compose_resource.TranslateResult.from_json(
            response.stdout[0]
        )
        log.debug('Successfully translated resources config to YAML.')
        log.debug(
            'YAML files:\n'
            f'{list(translate_result.services.values()) + list(translate_result.models.values())}'
        )
        for model_yaml in translate_result.models.values():
          compose_resource.deploy_application(
              yaml_file_path=model_yaml,
              region=region,
              args=args,
              release_track=release_track,
          )
        for service_yaml in translate_result.services.values():
          compose_resource.deploy_application(
              yaml_file_path=service_yaml,
              region=region,
              args=args,
              release_track=release_track,
          )
      else:
        log.error(f'Translate failed with error: {response.stderr}')
        raise exceptions.ConfigurationError(
            'Something went wrong while translating compose file to Cloud Run'
            ' service YAMLs.'
        )

      return response
    except Exception as e:
      log.error(f'Failed to handle resources config and translate to YAML: {e}')
      log.error(f'Raw output: {resource_response.stdout}')
      raise

  def Run(self, args):
    """Deploy a container from the source Compose file to Cloud Run."""
    log.status.Print('Deploying from Compose to Cloud Run...')
    region = flags.GetRegion(args, prompt=True)
    self._SetRegionConfig(region)
    project = properties.VALUES.core.project.Get(required=True)
    project_number = projects_util.GetProjectNumber(project)
    repo = self._GenerateRepositoryName(
        project,
        region,
    )
    docker_repo = docker_util.DockerRepo(
        project_id=project,
        location_id=region,
        repo_id=DEFAULT_REPO_NAME,
    )

    if artifact_registry.ShouldCreateRepository(
        docker_repo, skip_activation_prompt=True, skip_console_prompt=True
    ):
      self._CreateARRepository(docker_repo)

    command_executor = up.RunComposeWrapper()
    if args.compose_file:
      compose_file = args.compose_file
    else:
      compose_file = self._GetComposeFile()

    response = self._ResourceAndTranslateRun(
        command_executor, compose_file, repo, project_number, region, args
    )
    return response

  def _GenerateRepositoryName(self, project, region):
    """Generate a name for the repository."""
    repository = '{}-docker.pkg.dev'.format(region)
    return '{}/{}/{}'.format(
        repository, project.replace(':', '/'), DEFAULT_REPO_NAME
    )

  def _SetRegionConfig(self, region):
    """Set the region config."""
    if not properties.VALUES.run.region.Get():
      log.status.Print(
          'Region set to {region}.You can change the region with gcloud'
          ' config set run/region {region}.\n'.format(region=region)
      )
      properties.VALUES.run.region.Set(region)

  def _GetComposeFile(self):
    for filename in [
        'compose.yaml',
        'compose.yml',
        'docker-compose.yaml',
        'docker-compose.yml',
    ]:
      if os.path.exists(filename):
        return filename
    raise exceptions.ConfigurationError(
        'No compose file found. Please provide a compose file.'
    )

  def _CreateARRepository(self, docker_repo):
    """Create an Artifact Registry Repository if not present."""
    pretty_print.Success(
        f'Creating AR Repository in the region: {docker_repo.location}'
    )
    artifact_registry.CreateRepository(docker_repo, skip_activation_prompt=True)

  def _AddTrackerStages(self, config):
    """Add a tracker to the progress tracker."""
    staged_operations = []
    if config.source_builds:
      for container_name in config.source_builds:
        staged_operations.append(
            progress_tracker.Stage(
                f'Building container {container_name} from source...',
                key=stages.StagedProgressTrackerStage.BUILD.get_key(
                    container=container_name
                ),
            )
        )
    if config.secrets:
      staged_operations.append(
          progress_tracker.Stage(
              'Creating secrets...',
              key=stages.StagedProgressTrackerStage.SECRETS.get_key(),
          )
      )
    if config.volumes.bind_mount or config.volumes.named_volume:
      staged_operations.append(
          progress_tracker.Stage(
              'Creating volumes...',
              key=stages.StagedProgressTrackerStage.VOLUMES.get_key(),
          )
      )
    if config.configs:
      staged_operations.append(
          progress_tracker.Stage(
              'Creating configs...',
              key=stages.StagedProgressTrackerStage.CONFIGS.get_key(),
          )
      )
    return staged_operations
