# -*- coding: utf-8 -*- #
# Copyright 2013 Google LLC. All Rights Reserved.
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
"""Connects to a Cloud SQL instance."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import atexit
from apitools.base.py import exceptions as apitools_exceptions

from googlecloudsdk.api_lib.sql import api_util
from googlecloudsdk.api_lib.sql import constants
from googlecloudsdk.api_lib.sql import exceptions
from googlecloudsdk.api_lib.sql import instances as instances_api_util
from googlecloudsdk.api_lib.sql import network
from googlecloudsdk.api_lib.sql import operations
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.command_lib.sql import flags as sql_flags
from googlecloudsdk.command_lib.sql import instances as instances_command_util
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.util import files
from googlecloudsdk.core.util import iso_duration
from googlecloudsdk.core.util import retry
from googlecloudsdk.core.util import text
import six
import six.moves.http_client

EXAMPLES = (
    """\
    To connect to a Cloud SQL instance, run:

      $ {command} my-instance --user=root
    """
)

DETAILED_GA_HELP = {
    'DESCRIPTION':
        """
        Connects to a Cloud SQL instance.

        This command temporarily changes the authorized networks for this
        instance to allow the connection from your IP address.

        This command isn't supported for Cloud SQL instances with only
        private IP addresses.

        NOTE: If you're connecting from an IPv6 address, or are constrained by
        certain organization policies (restrictPublicIP,
        restrictAuthorizedNetworks), consider running the beta version of this
        command to avoid error by connecting through the Cloud SQL proxy:
        *gcloud beta sql connect*
        """,
    'EXAMPLES': EXAMPLES,
}

DETAILED_ALPHA_BETA_HELP = {
    'DESCRIPTION':
        """
        Connects to a Cloud SQL instance.
        """,
    'EXAMPLES': EXAMPLES,
}

# TODO(b/62055574): Improve test coverage in this file.


def _AllowlistClientIP(instance_ref,
                       sql_client,
                       sql_messages,
                       resources,
                       minutes=5):
  """Add CLIENT_IP to the authorized networks list.

  Makes an API call to add CLIENT_IP to the authorized networks list.
  The server knows to interpret the string CLIENT_IP as the address with which
  the client reaches the server. This IP will be allowlisted for 1 minute.

  Args:
    instance_ref: resources.Resource, The instance we're connecting to.
    sql_client: apitools.BaseApiClient, A working client for the sql version to
      be used.
    sql_messages: module, The module that defines the messages for the sql
      version to be used.
    resources: resources.Registry, The registry that can create resource refs
      for the sql version to be used.
    minutes: How long the client IP will be allowlisted for, in minutes.

  Returns:
    string, The name of the authorized network rule. Callers can use this name
    to find out the IP the client reached the server with.
  Raises:
    HttpException: An http error response was received while executing api
        request.
    ResourceNotFoundError: The SQL instance was not found.
  """
  time_of_connection = network.GetCurrentTime()

  acl_name = 'sql connect at time {0}'.format(time_of_connection)
  user_acl = sql_messages.AclEntry(
      kind='sql#aclEntry',
      name=acl_name,
      expirationTime=iso_duration.Duration(
          minutes=minutes).GetRelativeDateTime(time_of_connection)
      # TODO(b/122989827): Remove this once the datetime parsing is fixed.
      # Setting the microseconds component to 10 milliseconds. This complies
      # with backend formatting restrictions, since backend requires a microsecs
      # component and anything less than 1 milli will get truncated.
      .replace(microsecond=10000).isoformat(),
      value='CLIENT_IP')

  try:
    original = sql_client.instances.Get(
        sql_messages.SqlInstancesGetRequest(
            project=instance_ref.project, instance=instance_ref.instance))
  except apitools_exceptions.HttpError as error:
    if error.status_code == six.moves.http_client.FORBIDDEN:
      raise exceptions.ResourceNotFoundError(
          'There was no instance found at {} or you are not authorized to '
          'connect to it.'.format(instance_ref.RelativeName()))
    raise calliope_exceptions.HttpException(error)

  # TODO(b/122989827): Remove this once the datetime parsing is fixed.
  original.serverCaCert = None

  original.settings.ipConfiguration.authorizedNetworks.append(user_acl)
  try:
    patch_request = sql_messages.SqlInstancesPatchRequest(
        databaseInstance=original,
        project=instance_ref.project,
        instance=instance_ref.instance)
    result = sql_client.instances.Patch(patch_request)
  except apitools_exceptions.HttpError as error:
    log.warning(
        "If you're connecting from an IPv6 address, or are "
        "constrained by certain organization policies (restrictPublicIP, "
        "restrictAuthorizedNetworks), consider running the beta version of this "
        "command by connecting through the Cloud SQL proxy: "
        "gcloud beta sql connect")
    raise calliope_exceptions.HttpException(error)

  operation_ref = resources.Create(
      'sql.operations', operation=result.name, project=instance_ref.project)
  message = ('Allowlisting your IP for incoming connection for '
             '{0} {1}'.format(minutes, text.Pluralize(minutes, 'minute')))

  operations.OperationsV1Beta4.WaitForOperation(sql_client, operation_ref,
                                                message)

  return acl_name


def _GetClientIP(instance_ref, sql_client, acl_name):
  """Retrieves given instance and extracts its client ip."""
  instance_info = sql_client.instances.Get(
      sql_client.MESSAGES_MODULE.SqlInstancesGetRequest(
          project=instance_ref.project, instance=instance_ref.instance))
  networks = instance_info.settings.ipConfiguration.authorizedNetworks
  client_ip = None
  for net in networks:
    if net.name == acl_name:
      client_ip = net.value
      break
  return instance_info, client_ip


def AddBaseArgs(parser):
  """Declare flag and positional arguments for this command parser.

  Args:
      parser: An argparse parser that you can use it to add arguments that go on
        the command line after this command. Positional arguments are allowed.
  """
  parser.add_argument(
      'instance',
      completer=sql_flags.InstanceCompleter,
      help='Cloud SQL instance ID.')

  parser.add_argument(
      '--user',
      '-u',
      required=False,
      help='Cloud SQL instance user to connect as.')


def AddBetaArgs(parser):
  """Declare beta flag arguments for this command parser.

  Args:
      parser: An argparse parser that you can use it to add arguments that go on
        the command line after this command. Positional arguments are allowed.
  """
  parser.add_argument(
      '--port',
      type=arg_parsers.BoundedInt(lower_bound=1, upper_bound=65535),
      default=constants.DEFAULT_PROXY_PORT_NUMBER,
      help=('Port number that gcloud will use to connect to the Cloud SQL '
            'Proxy through localhost.'))


def AddProxyV2Args(parser) -> None:
  """Declare alpha flag arguments for this command parser.

  Args:
      parser: An argparse parser that you can use it to add arguments that go on
        the command line after this command. Positional arguments are allowed.
  """
  parser.add_argument(
      'instance',
      completer=sql_flags.InstanceCompleter,
      help='Cloud SQL instance ID.')

  parser.add_argument(
      '--port',
      type=arg_parsers.BoundedInt(lower_bound=1, upper_bound=65535),
      default=constants.DEFAULT_PROXY_PORT_NUMBER,
      help=('Port number that gcloud will use to connect to the Cloud SQL '
            'Proxy through localhost.'))
  user_group = parser.add_mutually_exclusive_group(
      'User selection settings for Cloud SQL Proxy connection.')
  user_group.add_argument(
      '--auto-iam-authn',
      action='store_true',
      help='Enables IAM database authentication for connections to MySQL and '
           'Postgres instances.')
  user_group.add_argument(
      '--user',
      '-u',
      required=False,
      help='Cloud SQL instance user to connect as.')
  parser.add_argument(
      '--skip-ssl',
      action='store_true',
      help='Skip SSL certificate verification for MySQL instances.')
  parser.add_argument(
      '--debug-logs',
      action='store_true',
      help='Enable verbose debug logs for Cloud SQL Proxy.')
  parser.add_argument(
      '--sqladmin-api-endpoint',
      help='Cloud SQL Admin API endpoint for Cloud SQL Proxy to use.')
  parser.add_argument(
      '--run-connection-test',
      action='store_true',
      help='Run connection test for Cloud SQL Proxy.')

  ip_group = parser.add_mutually_exclusive_group(
      'IP address selection settings for Cloud SQL Proxy connection.')
  ip_group.add_argument(
      '--private-ip',
      action='store_true',
      help='Connect to the Cloud SQL instance using private IP.')
  ip_group.add_argument(
      '--psc',
      action='store_true',
      help='Connect to the Cloud SQL instance using PSC.')
  ip_group.add_argument(
      '--auto-ip',
      action='store_true',
      help='Connect to the Cloud SQL instance with auto IP detection.')


def RunConnectCommand(args, supports_database=False):
  """Connects to a Cloud SQL instance directly.

  Args:
    args: argparse.Namespace, The arguments that this command was invoked with.
    supports_database: Whether or not the `--database` flag needs to be
      accounted for.

  Returns:
    If no exception is raised this method does not return. A new process is
    started and the original one is killed.
  Raises:
    HttpException: An http error response was received while executing api
        request.
    UpdateError: An error occurred while updating an instance.
    SqlClientNotFoundError: A local SQL client could not be found.
    ConnectionError: An error occurred while trying to connect to the instance.
  """
  client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
  sql_client = client.sql_client
  sql_messages = client.sql_messages

  instance_ref = instances_command_util.GetInstanceRef(args, client)

  acl_name = _AllowlistClientIP(instance_ref, sql_client, sql_messages,
                                client.resource_parser)

  # Get the client IP that the server sees. Sadly we can only do this by
  # checking the name of the authorized network rule.
  retryer = retry.Retryer(max_retrials=2, exponential_sleep_multiplier=2)
  try:
    instance_info, client_ip = retryer.RetryOnResult(
        _GetClientIP,
        [instance_ref, sql_client, acl_name],
        should_retry_if=lambda x, s: x[1] is None,  # client_ip is None
        sleep_ms=500)
  except retry.RetryException:
    raise exceptions.UpdateError('Could not allowlist client IP. Server did '
                                 'not reply with the allowlisted IP.')

  # Check for the mysql or psql executable based on the db version.
  db_type = instance_info.databaseVersion.name.split('_')[0]
  exe_name = constants.DB_EXE.get(db_type, 'mysql')
  exe = files.FindExecutableOnPath(exe_name)
  if not exe:
    raise exceptions.SqlClientNotFoundError(
        '{0} client not found.  Please install a {1} client and make sure '
        'it is in PATH to be able to connect to the database instance.'.format(
            exe_name.title(), exe_name))

  # Check the version of IP and decide if we need to add ipv4 support.
  ip_type = network.GetIpVersion(client_ip)
  if ip_type == network.IP_VERSION_4:
    if instance_info.settings.ipConfiguration.ipv4Enabled:
      ip_address = instance_info.ipAddresses[0].ipAddress
    else:
      # TODO(b/36049930): ask user if we should enable ipv4 addressing
      message = ('It seems your client does not have ipv6 connectivity and '
                 'the database instance does not have an ipv4 address. '
                 'Please request an ipv4 address for this database instance.')
      raise exceptions.ConnectionError(message)
  elif ip_type == network.IP_VERSION_6:
    ip_address = instance_info.ipv6Address
  else:
    raise exceptions.ConnectionError('Could not connect to SQL server.')

  # Determine what SQL user to connect with.
  sql_user = constants.DEFAULT_SQL_USER[exe_name]
  if args.user:
    sql_user = args.user

  # We have everything we need, time to party!
  flags = constants.EXE_FLAGS[exe_name]
  sql_args = [exe_name, flags['hostname'], ip_address]
  sql_args.extend([flags['user'], sql_user])
  if 'password' in flags:
    sql_args.append(flags['password'])

  if supports_database:
    sql_args.extend(instances_command_util.GetDatabaseArgs(args, flags))

  instances_command_util.ConnectToInstance(sql_args, sql_user)


def RunProxyConnectCommand(args,
                           supports_database=False):
  """Connects to a Cloud SQL instance through the Cloud SQL Proxy.

  Args:
    args: argparse.Namespace, The arguments that this command was invoked with.
    supports_database: Whether or not the `--database` flag needs to be
      accounted for.

  Returns:
    If no exception is raised this method does not return. A new process is
    started and the original one is killed.
  Raises:
    HttpException: An http error response was received while executing api
        request.
    CloudSqlProxyError: Cloud SQL Proxy could not be found.
    SqlClientNotFoundError: A local SQL client could not be found.
    ConnectionError: An error occurred while trying to connect to the instance.
  """
  client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
  sql_client = client.sql_client
  sql_messages = client.sql_messages

  instance_ref = instances_command_util.GetInstanceRef(args, client)

  instance_info = sql_client.instances.Get(
      sql_messages.SqlInstancesGetRequest(
          project=instance_ref.project, instance=instance_ref.instance))

  if not instances_api_util.IsInstanceV2(sql_messages, instance_info):
    # The Cloud SQL Proxy does not support V1 instances.
    return RunConnectCommand(args, supports_database)

  # If the instance is V2, keep going with the proxy.
  exe = files.FindExecutableOnPath('cloud_sql_proxy')
  if not exe:
    raise exceptions.CloudSqlProxyError(
        'Cloud SQL Proxy (v1) couldn\'t be found in PATH. Either install '
        'the component with `gcloud components install cloud_sql_proxy` or see '
        'https://github.com/GoogleCloudPlatform/cloud-sql-proxy/releases '
        'to install the v1 Cloud SQL Proxy. '
        'The v2 Cloud SQL Proxy is currently not supported by the '
        'connect command. You need to install the v1 Cloud SQL Proxy binary '
        'to use the connect command.')

  # Check for the executable based on the db version.
  db_type = instance_info.databaseVersion.name.split('_')[0]
  exe_name = constants.DB_EXE.get(db_type, 'mysql')
  exe = files.FindExecutableOnPath(exe_name)
  if not exe:
    raise exceptions.SqlClientNotFoundError(
        '{0} client not found.  Please install a {1} client and make sure '
        'it is in PATH to be able to connect to the database instance.'.format(
            exe_name.title(), exe_name))

  # Start the Cloud SQL Proxy and wait for it to be ready to accept connections.
  port = six.text_type(args.port)
  proxy_process = instances_api_util.StartCloudSqlProxy(instance_info, port)
  atexit.register(proxy_process.kill)

  # Determine what SQL user to connect with.
  sql_user = constants.DEFAULT_SQL_USER[exe_name]
  if args.user:
    sql_user = args.user

  # We have everything we need, time to party!
  flags = constants.EXE_FLAGS[exe_name]
  sql_args = [exe_name]
  if exe_name == 'sqlcmd':
    # sqlcmd merges hostname and port into a single argument
    hostname = 'tcp:127.0.0.1,{0}'.format(port)
    sql_args.extend([flags['hostname'], hostname])
  else:
    sql_args.extend([flags['hostname'], '127.0.0.1', flags['port'], port])
  sql_args.extend([flags['user'], sql_user])
  if 'password' in flags:
    sql_args.append(flags['password'])

  if supports_database:
    sql_args.extend(instances_command_util.GetDatabaseArgs(args, flags))

  instances_command_util.ConnectToInstance(sql_args, sql_user)
  proxy_process.kill()


def RunProxyV2ConnectCommand(args, supports_database=False):
  """Connects to a Cloud SQL instance through the Cloud SQL Proxy (v2).

  Args:
    args: argparse.Namespace, The arguments that this command was invoked with.
    supports_database: Whether or not the `--database` flag needs to be
      accounted for.

  Returns:
    If no exception is raised this method does not return. A new process is
    started and the original one is killed.
  Raises:
    HttpException: An http error response was received while executing api
        request.
    CloudSqlProxyError: Cloud SQL Proxy (v2) could not be found.
    SqlClientNotFoundError: A local SQL client could not be found.
    ConnectionError: An error occurred while trying to connect to the instance.
  """
  client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
  sql_client = client.sql_client
  sql_messages = client.sql_messages

  instance_ref = instances_command_util.GetInstanceRef(args, client)

  instance_info = sql_client.instances.Get(
      sql_messages.SqlInstancesGetRequest(
          project=instance_ref.project, instance=instance_ref.instance
      )
  )

  if not instances_api_util.IsInstanceV2(sql_messages, instance_info):
    # The Cloud SQL Proxy does not support V1 instances.
    return RunConnectCommand(args, supports_database)

  # If the instance is V2, keep going with the proxy.
  exe = files.FindExecutableOnPath('cloud-sql-proxy')
  if not exe:
    raise exceptions.CloudSqlProxyError(
        "Cloud SQL Proxy (v2) couldn't be found in PATH. Either install "
        'the component with `gcloud components install cloud-sql-proxy` or see '
        'https://github.com/GoogleCloudPlatform/cloud-sql-proxy/'
    )

  # Check for the executable based on the db version.
  db_type = instance_info.databaseVersion.name.split('_')[0]
  exe_name = constants.DB_EXE.get(db_type, 'mysql')
  exe = files.FindExecutableOnPath(exe_name)
  if not exe:
    raise exceptions.SqlClientNotFoundError(
        '{0} client not found.  Please install a {1} client and make sure '
        'it is in PATH to be able to connect to the database instance.'.format(
            exe_name.title(), exe_name
        )
    )

  auto_iam_authn = getattr(args, 'auto_iam_authn', False)
  if auto_iam_authn and exe_name == 'sqlcmd':
    raise calliope_exceptions.InvalidArgumentException(
        '--auto-iam-authn',
        'The --auto-iam-authn flag is only valid for MySQL and Postgres'
        ' instances.',
    )

  skip_ssl = getattr(args, 'skip_ssl', False)
  if skip_ssl and exe_name != 'mysql':
    raise calliope_exceptions.InvalidArgumentException(
        '--skip-ssl', 'The --skip-ssl flag is only valid for MySQL instances.'
    )

  # Start the Cloud SQL Proxy and wait for it to be ready to accept connections.
  port = str(args.port)
  impersonate_service_account = (
      properties.VALUES.auth.impersonate_service_account.Get()
  )
  private_ip = getattr(args, 'private_ip', False)
  psc = getattr(args, 'psc', False)
  auto_ip = getattr(args, 'auto_ip', False)
  debug_logs = getattr(args, 'debug_logs', False)
  sqladmin_api_endpoint = getattr(args, 'sqladmin_api_endpoint', None)
  run_connection_test = getattr(args, 'run_connection_test', False)
  proxy_process = instances_api_util.StartCloudSqlProxyV2(
      instance_info,
      port,
      impersonate_service_account=impersonate_service_account,
      auto_iam_authn=auto_iam_authn,
      private_ip=private_ip,
      psc=psc,
      auto_ip=auto_ip,
      debug_logs=debug_logs,
      sqladmin_api_endpoint=sqladmin_api_endpoint,
      run_connection_test=run_connection_test)
  atexit.register(proxy_process.kill)

  if run_connection_test:
    proxy_process.kill()
    return

  # Determine what database user to connect with.
  if auto_iam_authn:
    database_user = impersonate_service_account
    if not database_user:
      database_user = properties.VALUES.core.account.Get(required=True)
    if exe_name == 'mysql':
      # MySQL IAM db auth uses username without domain.
      database_user = database_user.split('@')[0]
    elif exe_name == 'psql' and database_user.endswith('.gserviceaccount.com'):
      # Postgres IAM db auth uses user@project.iam for service accounts.
      database_user = database_user.replace('.gserviceaccount.com', '')
  elif args.user:
    database_user = args.user
  else:
    database_user = constants.DEFAULT_SQL_USER[exe_name]

  # We have everything we need, time to party!
  flags = constants.EXE_FLAGS[exe_name]
  sql_args = [exe_name]
  if exe_name == 'sqlcmd':
    # sqlcmd merges hostname and port into a single argument
    hostname = 'tcp:127.0.0.1,{0}'.format(port)
    sql_args.extend([flags['hostname'], hostname])
  else:
    sql_args.extend([flags['hostname'], '127.0.0.1', flags['port'], port])
  sql_args.extend([flags['user'], database_user])
  if 'password' in flags and not auto_iam_authn:
    sql_args.append(flags['password'])

  if supports_database:
    if exe_name == 'mysql' and args.database:
      raise calliope_exceptions.InvalidArgumentException(
          '--database',
          'The --database flag is only valid for PostgreSQL or SQL Server'
          ' instances.',
      )
    db_args = instances_command_util.GetDatabaseArgs(args, flags)
    if not db_args and exe_name == 'psql':
      db_args = [flags['database'], 'postgres']
    sql_args.extend(db_args)

  if skip_ssl and exe_name == 'mysql':
    sql_args.append('--skip-ssl')

  instances_command_util.ConnectToInstance(sql_args, database_user)
  proxy_process.kill()


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Connect(base.Command):
  """Connects to a Cloud SQL instance."""

  detailed_help = DETAILED_GA_HELP

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command."""
    AddBaseArgs(parser)
    sql_flags.AddDatabase(
        parser, 'The SQL Server database to connect to.')

  def Run(self, args):
    """Connects to a Cloud SQL instance."""
    return RunConnectCommand(args, supports_database=True)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class ConnectBeta(base.Command):
  """Connects to a Cloud SQL instance."""

  detailed_help = DETAILED_ALPHA_BETA_HELP

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command."""
    AddBaseArgs(parser)
    AddBetaArgs(parser)
    sql_flags.AddDatabase(
        parser, 'The PostgreSQL or SQL Server database to connect to.')

  def Run(self, args):
    """Connects to a Cloud SQL instance."""
    return RunProxyConnectCommand(args, supports_database=True)


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ConnectAlpha(base.Command):
  """Connects to a Cloud SQL instance."""

  detailed_help = DETAILED_ALPHA_BETA_HELP

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command."""
    AddProxyV2Args(parser)
    sql_flags.AddDatabase(
        parser, 'The PostgreSQL or SQL Server database to connect to.'
    )

  def Run(self, args):
    """Connects to a Cloud SQL instance."""
    return RunProxyV2ConnectCommand(args, supports_database=True)
