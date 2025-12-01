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
"""Command to install on-premise Transfer agent."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import collections
import copy
import os
import shutil
import socket
import subprocess
import sys

from googlecloudsdk.api_lib.transfer import agent_pools_util
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.transfer import agents_util
from googlecloudsdk.command_lib.transfer import creds_util
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.credentials import gce_cache
from googlecloudsdk.core.universe_descriptor import universe_descriptor
from googlecloudsdk.core.util import platforms
from oauth2client import client as oauth2_client


COUNT_FLAG_HELP_TEXT = """
Specify the number of agents to install on your current machine.
System requirements: 8 GB of memory and 4 CPUs per agent.

Note: If the 'id-prefix' flag is specified, Transfer Service increments a number
value after each prefix. Example: prefix1, prefix2, etc.
"""
CREDS_FILE_FLAG_HELP_TEXT = """
Specify the path to the service account's credentials file.

No input required if authenticating with your user account credentials,
which Transfer Service will look for in your system.

Note that the credentials location will be mounted to the agent container.
"""
MOUNT_DIRECTORIES_HELP_TEXT = """
If you want to grant agents access to specific parts of your filesystem
instead of the entire filesystem, specify which directory paths to
mount to the agent container. Multiple paths must be separated by
commas with no spaces (e.g.,
--mount-directories=/system/path/to/dir1,/path/to/dir2). When mounting
specific directories, gcloud transfer will also mount a directory for
logs (either /tmp or what you've specified for --logs-directory) and
your Google credentials file for agent authentication.

It is strongly recommended that you use this flag. If this flag isn't specified,
gcloud transfer will mount your entire filesystem to the agent container and
give the agent root access.
"""
NETWORK_HELP_TEXT = """
Specify the network to connect the container to. This flag maps directly
to the `--network` flag in the underlying '{container_managers} run' command.

If binding directly to the host's network is an option, then setting this value
to 'host' can dramatically improve transfer performance.
"""
MISSING_PROJECT_ERROR_TEXT = """
Could not find project ID. Try adding the project flag: --project=[project-id]
"""
PROXY_FLAG_HELP_TEXT = """
Specify the HTTP URL and port of a proxy server if you want to use a forward
proxy. For example, to use the URL 'example.com' and port '8080' specify
'http://www.example.com:8080/'

Ensure that you specify the HTTP URL and not an HTTPS URL to avoid
double-wrapping requests in TLS encryption. Double-wrapped requests prevent the
proxy server from sending valid outbound requests.
"""

MISSING_CREDENTIALS_ERROR_TEXT = """
Credentials file not found at {creds_file_path}.

{fix_suggestion}.

Afterwards, re-run {executed_command}.
"""

CHECK_AGENT_CONNECTED_HELP_TEXT_FORMAT = """
To confirm your agents are connected, go to the following link in your browser,
and check that agent status is 'Connected' (it can take a moment for the status
to update and may require a page refresh):

https://console.cloud.google.com/transfer/on-premises/agent-pools/pool/\
{pool}/agents?project={project}

If your agent does not appear in the pool, check its local logs by running
"{logs_command}". The container ID is the string of random
characters printed by step [2/3]. The container ID can also be found by running
"{list_command}".
"""

S3_COMPATIBLE_HELP_TEXT = """
Allow the agent to work with S3-compatible sources. This flag blocks the
agent's ability to work with other source types (e.g., file systems).

When using this flag, you must provide source credentials either as
environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` or
as default credentials in your system's configuration files.

To provide credentials as environment variables, run:

```
AWS_ACCESS_KEY_ID="id" AWS_SECRET_ACCESS_KEY="secret" gcloud transfer agents install --s3-compatible-mode
```
"""

# Container manager installation guide URLs for the different container managers
# that are supported (currently Docker and Podman).
CONTAINER_MANAGER_INSTALLATION_GUIDE_URL_MAP = {
    agents_util.ContainerManager.DOCKER: collections.defaultdict(
        # Default guide URL when an OS-specific guide URL is not found.
        lambda: 'https://docs.docker.com/engine/install/',
        # OS-specific guide URLs.
        {
            platforms.OperatingSystem.LINUX: (
                'https://docs.docker.com/engine/install/'
            ),
            platforms.OperatingSystem.WINDOWS: (
                'https://docs.docker.com/engine/install/binaries/#install-server-and-client-binaries-on-windows'
            ),
            platforms.OperatingSystem.MACOSX: (
                'https://docs.docker.com/engine/install/binaries/#install-client-binaries-on-macos'
            ),
        },
    ),
    agents_util.ContainerManager.PODMAN: collections.defaultdict(
        # Default guide URL when an OS-specific guide URL is not found.
        lambda: 'https://podman.io/docs/installation/',
        # OS-specific guide URLs.
        {
            platforms.OperatingSystem.LINUX: (
                'https://podman.io/docs/installation/#installing-on-linux'
            ),
            platforms.OperatingSystem.WINDOWS: (
                'https://podman.io/docs/installation/#windows'
            ),
            platforms.OperatingSystem.MACOSX: (
                'https://podman.io/docs/installation/#macos'
            ),
        },
    ),
}

# Help text for when the container manager is not found.
CONTAINER_MANAGER_NOT_FOUND_HELP_TEXT = """
The agent runs inside a {container_manager} container, so you'll need
to install {container_manager} before finishing agent installation.

See the installation instructions at
{installation_guide_url} and re-run
'{executed_command}' after {container_manager} installation.
"""


def _get_container_subcommand(use_sudo, container_manager, subcommand):
  """Returns the container command for the given subcommand and container manager.

  Args:
    use_sudo (bool): Whether to use sudo in the command.
    container_manager (agents_util.ContainerManager): The container manager.
    subcommand (str): The subcommand to run.

  Returns:
    str: The container command for the given subcommand and container manager.
  """
  sudo_prefix = 'sudo ' if use_sudo else ''
  return (
      f'{sudo_prefix}{container_manager.value} container'
      f' {subcommand} [container ID]'
  )


def _expand_path(path):
  """Converts relative and symbolic paths to absolute paths.

  Args:
    path (str|None): The path to expand. If None, returns None.

  Returns:
    str|None: The absolute path or None if path is None.
  """
  if path is None:
    return None
  return os.path.abspath(os.path.expanduser(path))


def _get_executed_command():
  """Returns the run command. Does not include environment variables.

  Returns:
    str: The command that was executed by the user.
  """
  return ' '.join(sys.argv)


def _log_created_agent(command):
  """Logs the command used to create the agent.

  Args:
    command (list[str]): The command used to create the agent.
  """
  log.info('Created agent with command:\n{}'.format(' '.join(command)))


def _authenticate_and_get_creds_file_path(creds_file_supplied_by_user=None):
  """Ensures agent will be able to authenticate and returns creds.

  Args:
    creds_file_supplied_by_user (str): The path to the credentials file.

  Returns:
    str: The path to the credentials file.

  Raises:
    OSError: If the credentials file is not found.
  """
  # Can't disable near "else" (https://github.com/PyCQA/pylint/issues/872).
  # pylint:disable=protected-access
  if creds_file_supplied_by_user:
    creds_file_path = _expand_path(creds_file_supplied_by_user)
    if not os.path.exists(creds_file_path):
      fix_suggestion = (
          'Check for typos and ensure a creds file exists at the path')
      raise OSError(
          MISSING_CREDENTIALS_ERROR_TEXT.format(
              creds_file_path=creds_file_path,
              fix_suggestion=fix_suggestion,
              executed_command=_get_executed_command()))
    return creds_file_path

  creds_file_path = oauth2_client._get_well_known_file()
  # pylint:enable=protected-access
  if os.path.exists(creds_file_path):
    return creds_file_path

  if gce_cache.GetOnGCE(check_age=False):
    # GCE VMs allow user to authenticate via GCE metadata server.
    return None

  fix_suggestion = ('To generate a credentials file, please run'
                    ' `gcloud auth application-default login`')
  raise OSError(
      MISSING_CREDENTIALS_ERROR_TEXT.format(
          creds_file_path=creds_file_path,
          fix_suggestion=fix_suggestion,
          executed_command=_get_executed_command()))


def _check_if_container_manager_is_installed(
    container_manager=agents_util.ContainerManager.DOCKER,
):
  """Checks for binary identified by container_manager is in system PATH.

  Args:
    container_manager (agents_util.ContainerManager): The container manager.

  Raises:
    OSError: If the binary is not found.
  """
  command = container_manager.value
  if shutil.which(command):
    return

  # Raise a message that includes the installation guide URL.
  log.error('[2/3] {} not found'.format(command.title()))
  help_str = _get_help_text_for_container_manager_not_found(
      container_manager=container_manager,
      current_os=platforms.OperatingSystem(),
      executed_command=_get_executed_command(),
  )
  raise OSError(help_str)


# Pairs of user arg and container manager flag.
# Coincidence that it's just a case change.
_ADD_IF_PRESENT_PAIRS = [
    ('enable_multipart', '--enable-multipart'),
    ('hdfs_data_transfer_protection', '--hdfs-data-transfer-protection'),
    ('hdfs_namenode_uri', '--hdfs-namenode-uri'),
    ('hdfs_username', '--hdfs-username'),
    ('kerberos_config_file', '--kerberos-config-file'),
    ('kerberos_keytab_file', '--kerberos-keytab-file'),
    ('kerberos_service_principal', '--kerberos-service-principal'),
    ('kerberos_user_principal', '--kerberos-user-principal'),
    ('max_concurrent_small_file_uploads', '--entirefile-fr-parallelism'),
]


def _add_container_flag_if_user_arg_present(user_args, container_args):
  """Adds user flags values directly to Docker/Podman command.

  Args:
    user_args (argparse.Namespace): The user arguments.
    container_args (list[str]): The container arguments.
  """
  for user_arg, container_flag in _ADD_IF_PRESENT_PAIRS:
    user_value = getattr(user_args, user_arg, None)
    if user_value is not None:
      container_args.append('{}={}'.format(container_flag, user_value))


def _get_container_run_command(
    args, project, creds_file_path, elevate_privileges=False
):
  """Returns container run command from user arguments and generated values.

  When `elevate_privileges` is True, the command will be run with sudo and
  SELinux will be disabled by passing appropriate security-opt flags. This is
  needed for running the agent in a container that is not owned by the user.

  Args:
    args (argparse.Namespace): The user arguments.
    project (str): The project to use for the agent.
    creds_file_path (str): The path to the credentials file.
    elevate_privileges (bool): Whether to use sudo and disable SELinux.

  Returns:
    list[str]: The container run command.
  """
  base_container_command = []
  if elevate_privileges:
    base_container_command.append('sudo')

  container_manager = agents_util.ContainerManager.from_args(args)
  base_container_command.extend([
      container_manager.value,
      'run',
      '--ulimit',
      'memlock={}'.format(args.memlock_limit),
      '--rm',
      '-d',
  ])

  aws_access_key, aws_secret_key = creds_util.get_default_aws_creds()
  if aws_access_key:
    base_container_command.append('--env')
    base_container_command.append('AWS_ACCESS_KEY_ID={}'.format(aws_access_key))
  if aws_secret_key:
    base_container_command.append('--env')
    base_container_command.append(
        'AWS_SECRET_ACCESS_KEY={}'.format(aws_secret_key)
    )
  if args.network:
    base_container_command.append('--network={}'.format(args.network))

  expanded_creds_file_path = _expand_path(creds_file_path)
  expanded_logs_directory_path = _expand_path(args.logs_directory)

  root_with_drive = os.path.abspath(os.sep)
  root_without_drive = os.sep
  mount_entire_filesystem = (
      not args.mount_directories
      or root_with_drive in args.mount_directories
      or root_without_drive in args.mount_directories
  )
  if mount_entire_filesystem:
    base_container_command.append('-v=/:/transfer_root')
  else:
    # Mount mandatory directories.
    mount_flags = [
        '-v={}:/tmp'.format(expanded_logs_directory_path),
    ]
    if expanded_creds_file_path is not None:
      mount_flags.append(
          '-v={creds_file_path}:{creds_file_path}'.format(
              creds_file_path=expanded_creds_file_path),
      )
    for path in args.mount_directories:
      # Mount custom directory.
      mount_flags.append('-v={path}:{path}'.format(path=path))
    base_container_command.extend(mount_flags)

  if args.proxy:
    base_container_command.append('--env')
    base_container_command.append('HTTPS_PROXY={}'.format(args.proxy))

  # default docker_uri_prefix is gcr.io/
  docker_uri_prefix = 'gcr.io/'

  if not properties.IsDefaultUniverse():
    universe_descriptor_obj = universe_descriptor.GetUniverseDomainDescriptor()
    docker_uri_prefix = (
        f'docker.{universe_descriptor_obj.artifact_registry_domain}'
        f'/{universe_descriptor_obj.project_prefix}/cloud-ingest/'
    )

  agent_args = [
      f'{docker_uri_prefix}cloud-ingest/tsop-agent:latest',
      '--agent-pool={}'.format(args.pool),
      '--hostname={}'.format(socket.gethostname()),
      '--log-dir={}'.format(expanded_logs_directory_path),
      '--project-id={}'.format(project),
  ]
  if expanded_creds_file_path is not None:
    agent_args.append('--creds-file={}'.format(expanded_creds_file_path))
  if mount_entire_filesystem:
    agent_args.append('--enable-mount-directory')
  if args.id_prefix:
    if args.count is not None:
      agent_id_prefix = args.id_prefix + '0'
    else:
      agent_id_prefix = args.id_prefix
    agent_args.append('--agent-id-prefix={}'.format(agent_id_prefix))
  gcs_api_endpoint = getattr(args, 'gcs_api_endpoint', None)
  if gcs_api_endpoint:
    agent_args.append('--gcs-api-endpoint={}'.format(gcs_api_endpoint))

  _add_container_flag_if_user_arg_present(args, agent_args)

  if args.s3_compatible_mode:
    # TODO(b/238213039): Remove when this flag becomes optional.
    agent_args.append('--enable-s3')

  # Propagate universe domain to the agent if available.
  if not properties.IsDefaultUniverse():
    universe_domain = properties.VALUES.core.universe_domain.Get()
    agent_args.append('--universe-domain={}'.format(universe_domain))

  return base_container_command + agent_args


def _execute_container_command(args, project, creds_file_path):
  """Generates, executes, and returns agent install and run command.

  Args:
    args (argparse.Namespace): The user arguments.
    project (str): The project to use for the agent.
    creds_file_path (str): The path to the credentials file.

  Returns:
    list[str]: The container run command.

  Raises:
    OSError: If the command fails to execute.
  """
  container_run_command = _get_container_run_command(
      args, project, creds_file_path
  )

  completed_process = subprocess.run(container_run_command, check=False)
  if completed_process.returncode == 0:
    _log_created_agent(container_run_command)
    return container_run_command

  container_manager = agents_util.ContainerManager.from_args(args)
  log.status.Print(
      '\nCould not execute {} command. Trying with "sudo".'.format(
          container_manager.value.title()
      )
  )
  elevated_privileges_container_run_command = _get_container_run_command(
      args, project, creds_file_path, elevate_privileges=True
  )
  elevated_prev_completed_process = subprocess.run(
      elevated_privileges_container_run_command, check=False
  )
  if elevated_prev_completed_process.returncode == 0:
    _log_created_agent(elevated_privileges_container_run_command)
    return elevated_privileges_container_run_command
  command_str = ' '.join(container_run_command)
  raise OSError(f'Error executing command:\n{command_str}')


def _create_additional_agents(agent_count, agent_id_prefix, container_command):
  """Creates multiple identical agents.

  Args:
    agent_count (int): The number of agents to create.
    agent_id_prefix (str): The prefix to add to the agent ID.
    container_command (list[str]): The container command to execute.
  """

  # Find the index of the --agent-id-prefix flag in the docker command.
  idx_agent_prefix = -1
  for idx, token in enumerate(container_command):
    if token.startswith('--agent-id-prefix='):
      idx_agent_prefix = idx
      break

  for count in range(1, agent_count):
    # container_command is a list, so copy to avoid mutating the original.
    container_command_copy = copy.deepcopy(container_command)
    if agent_id_prefix:
      # Since agent_id_prefix is not None, we know that idx_agent_prefix is not
      # -1.
      container_command_copy[idx_agent_prefix] = (
          '--agent-id-prefix={}{}'.format(agent_id_prefix, str(count))
      )
    # Less error handling than before. Just propogate any process errors.
    subprocess.run(container_command_copy, check=True)
    _log_created_agent(container_command_copy)


def _get_help_text_for_container_manager_not_found(
    container_manager, current_os, executed_command
):
  """Returns the help text for when the container manager is not found.

  Args:
    container_manager (agents_util.ContainerManager): The container manager.
    current_os (platforms.OperatingSystem): The current operating system.
    executed_command (str): The command that was executed.

  Returns:
    str: The help text for when the container manager is not found.

  Raises:
    ValueError: If the container manager is not supported.
  """
  if container_manager not in CONTAINER_MANAGER_INSTALLATION_GUIDE_URL_MAP:
    raise ValueError(f'Container manager not supported: {container_manager}')

  # Get OS-specific installation guide URL for container manager.
  installation_guide_url = CONTAINER_MANAGER_INSTALLATION_GUIDE_URL_MAP[
      container_manager
  ][current_os]

  return CONTAINER_MANAGER_NOT_FOUND_HELP_TEXT.format(
      container_manager=container_manager.value.title(),
      installation_guide_url=installation_guide_url,
      executed_command=executed_command,
  )


INSTALL_CMD_DESCRIPTION_TEXT = """\
    Install Transfer Service agents to enable you to transfer data to or from
    POSIX filesystems, such as on-premises filesystems. Agents are installed
    locally on your machine and run inside {container_managers} containers.
"""

INSTALL_CMD_EXAMPLES_TEXT = """\
    To create an agent pool for your agent, see the
    `gcloud transfer agent-pools create` command.

    To install an agent that authenticates with your user account credentials
    and has default agent parameters, run:

      $ {command} --pool=AGENT_POOL

    You will be prompted to run a command to generate a credentials file if
    one does not already exist.

    To install an agent that authenticates with a service account with
    credentials stored at '/example/path.json', run:

      $ {command} --creds-file=/example/path.json --pool=AGENT_POOL

    To install an agent using service account impersonation, run:

      $ {command} --creds-file=/example/path.json --pool=CUSTOM_AGENT_POOL --impersonate-service-account=impersonated-account@project-id.iam.gserviceaccount.com

    Note : The `--impersonate-service-account` flag only applies to the API
    calls made by gcloud during the agent installation and authorization process.
    The impersonated credentials are not passed to the transfer agent's runtime
    environment. The agent itself does not support impersonation and will use
    the credentials provided via the `--creds-file` flag or the default gcloud
    authenticated account for all of its operations. To grant the agent permissions,
    you must provide a service account key with the required direct roles
    (e.g., Storage Transfer Agent, Storage Object User)
"""


def _get_detailed_help_text(release_track):
  """Returns the detailed help dictionary for the install command based on the release track.

  Args:
    release_track (base.ReleaseTrack): The release track.

  Returns:
    dict[str, str]: The detailed help dictionary for the install command.
  """
  is_alpha = release_track == base.ReleaseTrack.ALPHA
  container_managers = 'Docker or Podman' if is_alpha else 'Docker'
  description_text = INSTALL_CMD_DESCRIPTION_TEXT.format(
      container_managers=container_managers
  )
  return {
      'DESCRIPTION': description_text,
      'EXAMPLES': INSTALL_CMD_EXAMPLES_TEXT,
  }


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Install(base.Command):
  """Install Transfer Service agents."""

  detailed_help = _get_detailed_help_text(base.ReleaseTrack.GA)

  @staticmethod
  def Args(parser, release_track=base.ReleaseTrack.GA):
    """Add arguments for the install command.

    Args:
      parser (argparse.ArgumentParser): The argument parser for the command.
      release_track (base.ReleaseTrack): The release track.
    """
    parser.add_argument(
        '--pool',
        required=True,
        help='The agent pool to associate with the newly installed agent.'
        ' When creating transfer jobs, the agent pool parameter will determine'
        ' which agents are activated.')
    parser.add_argument('--count', type=int, help=COUNT_FLAG_HELP_TEXT)
    parser.add_argument('--creds-file', help=CREDS_FILE_FLAG_HELP_TEXT)
    # The flag --docker-network is only supported in GA and will eventually
    # be replaced by the --network flag.
    if release_track == base.ReleaseTrack.GA:
      parser.add_argument(
          '--docker-network',
          dest='network',
          help=NETWORK_HELP_TEXT.format(container_managers='docker'),
      )
    parser.add_argument(
        '--enable-multipart',
        action=arg_parsers.StoreTrueFalseAction,
        help='Split up files and transfer the resulting chunks in parallel'
        ' before merging them at the destination. Can be used make transfers of'
        ' large files faster as long as the network and disk speed are not'
        ' limiting factors. If unset, agent decides when to use the feature.')
    parser.add_argument(
        '--id-prefix',
        help='An optional prefix to add to the agent ID to help identify the'
        ' agent.')
    parser.add_argument(
        '--logs-directory',
        default='/tmp',
        help='Specify the absolute path to the directory you want to store'
        ' transfer logs in. If not specified, gcloud transfer will mount your'
        ' /tmp directory for logs.')
    parser.add_argument(
        '--memlock-limit',
        default=64000000,
        type=int,
        help="Set the agent container's memlock limit. A value of 64000000"
        ' (default) or higher is required to ensure that agent versions'
        ' 1.14 or later have enough locked memory to be able to start.')
    parser.add_argument(
        '--mount-directories',
        type=arg_parsers.ArgList(),
        metavar='MOUNT-DIRECTORIES',
        help=MOUNT_DIRECTORIES_HELP_TEXT,
    )
    parser.add_argument('--proxy', help=PROXY_FLAG_HELP_TEXT)
    parser.add_argument(
        '--s3-compatible-mode',
        action='store_true',
        help=S3_COMPATIBLE_HELP_TEXT)

    hdfs_group = parser.add_group(
        category='HDFS',
        sort_args=False,
    )
    hdfs_group.add_argument(
        '--hdfs-namenode-uri',
        help=(
            'A URI representing an HDFS cluster including a schema, namenode,'
            ' and port. Examples: "rpc://my-namenode:8020",'
            ' "http://my-namenode:9870".\n\nUse "http" or "https" for WebHDFS.'
            ' If no schema is'
            ' provided, the CLI assumes native "rpc". If no port is provided,'
            ' the default is 8020 for RPC, 9870 for HTTP, and 9871 for HTTPS.'
            ' For example, the input "my-namenode" becomes'
            ' "rpc://my-namenode:8020".'
        ),
    )
    hdfs_group.add_argument(
        '--hdfs-username',
        help='Username for connecting to an HDFS cluster with simple auth.',
    )
    hdfs_group.add_argument(
        '--hdfs-data-transfer-protection',
        choices=['authentication', 'integrity', 'privacy'],
        help=(
            'Client-side quality of protection setting for Kerberized clusters.'
            ' Client-side QOP value cannot be more restrictive than the'
            ' server-side QOP value.'
        ),
    )

    kerberos_group = parser.add_group(
        category='Kerberos',
        sort_args=False,
    )
    kerberos_group.add_argument(
        '--kerberos-config-file', help='Path to Kerberos config file.'
    )
    kerberos_group.add_argument(
        '--kerberos-keytab-file',
        help=(
            'Path to a Keytab file containing the user principal specified'
            ' with the --kerberos-user-principal flag.'
        ),
    )
    kerberos_group.add_argument(
        '--kerberos-user-principal',
        help=(
            'Kerberos user principal to use when connecting to an HDFS cluster'
            ' via Kerberos auth.'
        ),
    )
    kerberos_group.add_argument(
        '--kerberos-service-principal',
        help=(
            'Kerberos service principal to use, of the form'
            ' "<primary>/<instance>". Realm is mapped from your Kerberos'
            ' config. Any supplied realm is ignored. If not passed in, it will'
            ' default to "hdfs/<namenode_fqdn>" (fqdn = fully qualified domain'
            ' name).'
        ),
    )

  def Run(self, args):
    """Installs the agent.

    Args:
      args (argparse.Namespace): The arguments to the command.
    """
    if args.count is not None and args.count < 1:
      raise ValueError('Agent count must be greater than zero.')

    project = properties.VALUES.core.project.Get()
    if not project:
      raise ValueError(MISSING_PROJECT_ERROR_TEXT)

    messages = apis.GetMessagesModule('transfer', 'v1')
    if (agent_pools_util.api_get(args.pool).state !=
        messages.AgentPool.StateValueValuesEnum.CREATED):
      raise ValueError('Agent pool not found: ' + args.pool)

    creds_file_path = _authenticate_and_get_creds_file_path(args.creds_file)
    log.status.Print('[1/3] Credentials found ✓')

    # Get the container_manager attribute on args, or default to Docker
    # because we are in the GA surface, we need to be resilient to the
    # container_manager flag not being present.
    container_manager = agents_util.ContainerManager.from_args(args)

    _check_if_container_manager_is_installed(container_manager)
    log.status.Print('[2/3] {} found ✓'.format(container_manager.value.title()))

    container_command = _execute_container_command(
        args, project, creds_file_path
    )
    if args.count is not None:
      _create_additional_agents(args.count, args.id_prefix, container_command)
    log.status.Print('[3/3] Agent installation complete! ✓')

    # If the user ran the command with sudo, we need to use sudo for the
    # subsequent commands (logs and list).
    use_sudo = container_command[0] == 'sudo'

    log.status.Print(
        CHECK_AGENT_CONNECTED_HELP_TEXT_FORMAT.format(
            pool=args.pool,
            project=project,
            logs_command=_get_container_subcommand(
                use_sudo,
                container_manager,
                'logs',
            ),
            list_command=_get_container_subcommand(
                use_sudo,
                container_manager,
                'list',
            ),
        )
    )


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class InstallAlpha(Install):
  """Install Transfer Service agents."""

  detailed_help = _get_detailed_help_text(base.ReleaseTrack.ALPHA)

  @staticmethod
  def Args(parser):
    """Add arguments for the install command.

    Args:
      parser (argparse.ArgumentParser): The argument parser for the command.
    """
    Install.Args(parser, release_track=base.ReleaseTrack.ALPHA)
    parser.add_argument(
        '--max-concurrent-small-file-uploads',
        type=int,
        help='Adjust the maximum number of files less than or equal to 32 MiB'
        ' large that the agent can upload in parallel. Not recommended for'
        " users unfamiliar with Google Cloud's rate limiting.")
    # podman is available in alpha only but the wiring to make it work in GA
    # is already in place.
    parser.add_argument(
        '--container-manager',
        choices=sorted(
            [option.value for option in agents_util.ContainerManager]
        ),
        default=agents_util.ContainerManager.DOCKER.value,
        help='The container manager to use for running agents.',
    )
    # --network is the new name for the --docker-network flag, once we are ready
    # to deprecate and eventually remove the --docker-network flag.
    parser.add_argument(
        '--network',
        dest='network',
        help=NETWORK_HELP_TEXT.format(container_managers='(docker or podman)'),
    )
    parser.add_argument(
        '--gcs-api-endpoint',
        help=(
            'The API endpoint for Google Cloud Storage. Override to use a'
            ' regional endpoint, ensuring data remains within designated'
            ' geographic boundaries.'
        ),
    )
