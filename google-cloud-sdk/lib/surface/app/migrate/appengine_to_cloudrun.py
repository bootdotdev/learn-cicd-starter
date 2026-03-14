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

"""The gcloud app migrate appengine-to-cloudrun command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import collections
import re

from googlecloudsdk.api_lib.app import appengine_api_client
from googlecloudsdk.api_lib.run import k8s_object
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.app import gae_to_cr_migration_util
from googlecloudsdk.command_lib.app.gae_to_cr_migration_util import list_incompatible_features
from googlecloudsdk.command_lib.app.gae_to_cr_migration_util import translate
from googlecloudsdk.command_lib.run import config_changes
from googlecloudsdk.command_lib.run import flags
from surface.run import deploy


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AppEngineToCloudRun(deploy.AlphaDeploy):
  """Migrate the second-generation App Engine app to Cloud Run."""

  detailed_help = {
      'DESCRIPTION': """\
          Migrates the second-generation App Engine app to Cloud Run.
          """,
      'EXAMPLES': """\
          To migrate an App Engine app to Cloud Run:\n
          through app.yaml\n
          gcloud app migrate appengine-to-cloudrun --appyaml=path/to/app.yaml --entrypoint=main\n
          OR\n
          through service and version\n
          gcloud app migrate appengine-to-cloudrun --service=default --version=v1 --entrypoint=main\n
          """,
  }

  @classmethod
  def Args(cls, parser):
    super().Args(parser)
    parser.add_argument(
        '--appyaml',
        help=(
            'YAML file for the second generation App Engine version to be'
            ' migrated.'
        ),
    )
    parser.add_argument(
        '--service',
        help='service name that is deployed in App Engine',
    )
    parser.add_argument(
        '--version',
        help='version name that is deployed in App Engine',
    )
    parser.add_argument(
        '--entrypoint',
        help='entrypoint required for some runtimes',
    )

  @base.DefaultUniverseOnly
  @base.ReleaseTracks(base.ReleaseTrack.ALPHA)
  def Run(self, args):
    """Overrides the Deploy.Run method, applying the wrapper logic for FlagIsExplicitlySet.
    """
    api_client = appengine_api_client.GetApiClientForTrack(self.ReleaseTrack())
    gae_to_cr_migration_util.GAEToCRMigrationUtil(
        api_client, args
    )
    self.release_track = self.ReleaseTrack()
    original_flag_is_explicitly_set = flags.FlagIsExplicitlySet
    try:
      flags.FlagIsExplicitlySet = self._flag_is_explicitly_set_wrapper
      self.StartMigration(args)
      super().Run(args)
    finally:
      flags.FlagIsExplicitlySet = original_flag_is_explicitly_set

  def _flag_is_explicitly_set_wrapper(self, args, flag):
    """Wrapper function to check if a flag is explicitly set.

    This wrapper checks for flags added during the migration process,
    in addition to the original flags.FlagIsExplicitlySet check.

    Args:
      args: The arguments to check.
      flag: The flag to check.

    Returns:
      bool: True if the flag is explicitly set, False otherwise.
    """
    return (
        hasattr(self, '_migration_flags') and flag in self._migration_flags
    )

  def _GetBaseChanges(self, args):
    """Returns the service config changes with some default settings."""
    changes = flags.GetServiceConfigurationChanges(args, self.ReleaseTrack())
    changes.insert(
        0,
        config_changes.DeleteAnnotationChange(
            k8s_object.BINAUTHZ_BREAKGLASS_ANNOTATION
        ),
    )
    changes.append(
        config_changes.SetLaunchStageAnnotationChange(base.ReleaseTrack.ALPHA)
    )
    return changes

  def StartMigration(self, args) -> None:
    """Starts the migration process."""

    # List incompatible features.
    list_incompatible_features.list_incompatible_features(
        args.appyaml, args.service, args.version
    )

    # Translate app.yaml to gcloud run deploy flags.
    cloud_run_deploy_command = translate.translate(
        args.appyaml, args.service, args.version, args.entrypoint
    )
    print_deploy_command = ''
    for command_str in cloud_run_deploy_command:
      if command_str.startswith('--labels'):
        command_str = '--labels=migrated-from=app-engine,migration-tool=gcloud-app-migrate-standard-v1'
      print_deploy_command += command_str + ' '
    if args.entrypoint:
      setattr(
          args,
          'set-build-env-vars',
          {'GOOGLE_ENTRYPOINT': args.entrypoint},
      )
      print_deploy_command += (
          ' --set-build-env-vars GOOGLE_ENTRYPOINT=gunicorn -b :$PORT main:app'
      )

    # Run gcloud run deploy command.
    print('Command to run:', print_deploy_command, '\n')
    setattr(args, 'SERVICE', cloud_run_deploy_command[3])
    self._migration_flags = []
    for command_str in cloud_run_deploy_command:
      if command_str.startswith('--'):
        command_str = command_str.replace('--', '')
        # TODO: b/445905035 - Use ArgDict type for args to simplify the parsing
        # logic
        command_args = command_str.split('=')
        command_args[0] = command_args[0].replace('-', '_')
        self._migration_flags.append(command_args[0])
        if command_args[0] == 'labels':
          args.__setattr__(
              command_args[0],
              {
                  'migrated-from': 'app-engine',
                  'migration-tool': 'gcloud-app-migrate-standard-v1',
              },
          )
          continue
        if command_args[0] == 'set_env_vars':
          args.__setattr__(command_args[0], self.ParseSetEnvVars(command_str))
          continue
        if command_args[0] == 'timeout':
          if command_args[1] == '600':
            args.__setattr__(command_args[0], 600)
          elif command_args[1] == '3600':
            args.__setattr__(command_args[0], 3600)
          continue
        if command_args[0] == 'min_instances':
          args.__setattr__(command_args[0], flags.ScaleValue(command_args[1]))
          continue
        if command_args[0] == 'max_instances':
          args.__setattr__(command_args[0], flags.ScaleValue(command_args[1]))
          continue
        if len(command_args) > 1:
          args.__setattr__(command_args[0], command_args[1])
        else:
          args.__setattr__(command_args[0], True)
    return

  def ParseSetEnvVars(
      self, input_str: str
  ) -> collections.OrderedDict[str, str]:
    """Parses a 'set-env-vars' string and converts it into an OrderedDict.

    Args:
        input_str: A string in the format of
          'set-env-vars="KEY1=VALUE1,KEY2=VALUE2"'.

    Returns:
        An OrderedDict containing the environment variables.
    """
    match = re.search(r'="([^"]*)"', input_str)

    if not match:
      return collections.OrderedDict()
    vars_string = match.group(1)

    if not vars_string:
      return collections.OrderedDict()

    env_vars = collections.OrderedDict(
        pair.split('=', 1) for pair in vars_string.split(',')
    )
    return env_vars

