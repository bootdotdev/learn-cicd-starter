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
"""Updates a user's database roles in a given instance."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.sql import api_util
from googlecloudsdk.api_lib.sql import instances as instances_api_util
from googlecloudsdk.api_lib.sql import operations
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.sql import flags
from googlecloudsdk.command_lib.sql import users
from googlecloudsdk.core import properties


DETAILED_HELP = {
    'DESCRIPTION':
        '{description}',
    'EXAMPLES':
        """\
          To grant database roles ``role1'' and ``role2'' for ``my-user'' in instance ``prod-instance'', run:

            $ {command} my-user --instance=prod-instance --database-roles=role1,role2 --type=BUILT_IN

          To revoke existing database roles and grant new database roles ``role3'' and ``role4'' for ``my-user'' in instance
          ``prod-instance'', run:

            $ {command} my-user --instance=prod-instance --revoke-existing-roles --database-roles=role3,role4 --type=BUILT_IN
          """,
}


def AddBaseArgs(parser):
  """Args is called by calliope to gather arguments for this command.

  Args:
    parser: An argparse parser that you can use it to add arguments that go on
      the command line after this command. Positional arguments are allowed.
  """
  flags.AddInstance(parser)
  flags.AddUsername(parser)
  flags.AddHost(parser)
  flags.AddType(parser, required=True)
  flags.AddDatabaseRoles(parser)
  flags.AddRevokeExistingRoles(parser)
  parser.display_info.AddCacheUpdater(None)


def AddBetaArgs(parser):
  del parser  # Unused.
  pass


def AddAlphaArgs(parser):
  del parser  # Unused.
  pass


def RunBaseAssignRolesCommand(args):
  """Updates a user's database roles in a given instance.

  Args:
    args: argparse.Namespace, The arguments that this command was invoked
      with.

  Returns:
    SQL user resource iterator.
  """
  client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
  sql_client = client.sql_client
  sql_messages = client.sql_messages

  instance_ref = client.resource_parser.Parse(
      args.instance,
      params={'project': properties.VALUES.core.project.GetOrFail},
      collection='sql.instances',
  )

  instance = sql_client.instances.Get(
      sql_messages.SqlInstancesGetRequest(
          project=instance_ref.project, instance=instance_ref.instance
      )
  )
  is_mysql = instances_api_util.InstancesV1Beta4.IsMysqlDatabaseVersion(
      instance.databaseVersion
  )
  name = args.username
  host = args.host
  user_type = users.ParseUserType(sql_messages, args)
  if (
      user_type == sql_messages.User.TypeValueValuesEnum.CLOUD_IAM_GROUP
      and is_mysql
  ):
    # MySQL IAM groups are stored with the domain in the host field.
    if '@' not in name:
      raise exceptions.InvalidArgumentException(
          'username',
          message=(
              'Cloud SQL IAM groups must be specified with the domain name in'
              ' the username field.'
          ),
      )
    host = name.split('@')[1]
    name = name.split('@')[0]

  user = sql_client.users.Get(
      sql_messages.SqlUsersGetRequest(
          project=instance_ref.project,
          instance=args.instance,
          name=name,
          host=host,
      )
  )

  user_type = user.type
  name = user.name
  if (
      user_type == sql_messages.User.TypeValueValuesEnum.CLOUD_IAM_USER
      or user_type
      == sql_messages.User.TypeValueValuesEnum.CLOUD_IAM_SERVICE_ACCOUNT
      or user_type
      == sql_messages.User.TypeValueValuesEnum.CLOUD_IAM_GROUP
  ):
    # For MySQL, the iam email needs to be passed in as the name.
    if user.iamEmail:
      name = user.iamEmail
    # For MySQL IAM users, the host is not supported.
    host = ''

  result_operation = sql_client.users.Update(
      sql_messages.SqlUsersUpdateRequest(
          project=instance_ref.project,
          instance=args.instance,
          name=name,
          host=host,
          user=sql_messages.User(
              project=instance_ref.project,
              instance=args.instance,
              name=name,
              type=user.type),
          databaseRoles=args.database_roles,
          revokeExistingRoles=args.revoke_existing_roles))
  operation_ref = client.resource_parser.Create(
      'sql.operations',
      operation=result_operation.name,
      project=instance_ref.project)
  if args.async_:
    return sql_client.operations.Get(
        sql_messages.SqlOperationsGetRequest(
            project=operation_ref.project, operation=operation_ref.operation))
  operations.OperationsV1Beta4.WaitForOperation(sql_client, operation_ref,
                                                'Updating Cloud SQL user')


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
@base.Hidden
class AssignRoles(base.UpdateCommand):
  """Updates a user's database roles in a given instance.

  Updates a user's database roles in a given instance with a specified
  username and host.
  """

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use it to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    AddBaseArgs(parser)
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    return RunBaseAssignRolesCommand(args)


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.UniverseCompatible
@base.Hidden
class AssignRolesBeta(base.UpdateCommand):
  """Updates a user's database roles in a given instance.

  Updates a user's database roles in a given instance with a specified
  username and host.
  """

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use it to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    AddBetaArgs(parser)
    AddBaseArgs(parser)
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    return RunBaseAssignRolesCommand(args)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
@base.Hidden
class AssignRolesAlpha(base.UpdateCommand):
  """Updates a user's database roles in a given instance.

  Updates a user's database roles in a given instance with a specified
  username and host.
  """

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use it to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    AddAlphaArgs(parser)
    AddBetaArgs(parser)
    AddBaseArgs(parser)
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    return RunBaseAssignRolesCommand(args)
