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
"""Performs a point in time restore for a Cloud SQL instance managed by Google Cloud Backup and Disaster Recovery."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.sql import api_util
from googlecloudsdk.api_lib.sql import operations
from googlecloudsdk.api_lib.sql import validate
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import parser_extensions
from googlecloudsdk.command_lib.sql import constants
from googlecloudsdk.command_lib.sql import flags
from googlecloudsdk.command_lib.sql import instances as command_util
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources
from googlecloudsdk.generated_clients.apis.sqladmin.v1beta4 import sqladmin_v1beta4_messages


DESCRIPTION = """\

    *{command}* performs a point in time restore for a Cloud SQL instance
    managed by Google Cloud Backup and Disaster Recovery.

    """

EXAMPLES_GA = """\
    To perform a point in time restore from an earlier point in time:

      $ {command} datasource target-instance '2012-11-15T16:19:00.094Z'

    """

DETAILED_HELP = {
    'DESCRIPTION': DESCRIPTION,
    'EXAMPLES': EXAMPLES_GA,
}


def _GetInstanceRefFromArgs(
    args: parser_extensions.Namespace, client: api_util.SqlClient
) -> resources.Resource:
  """Get validated ref to destination instance from args."""

  validate.ValidateInstanceName(args.target)
  return client.resource_parser.Parse(
      args.target,
      params={'project': properties.VALUES.core.project.GetOrFail},
      collection='sql.instances',
  )


def _UpdateRequestFromArgs(
    request: sqladmin_v1beta4_messages.SqlInstancesPointInTimeRestoreRequest,
    args: parser_extensions.Namespace,
) -> None:
  """Update request with clone options."""
  pitr_context = request.pointInTimeRestoreContext
  if args.restore_database_names:
    pitr_context.databaseNames[:] = [args.restore_database_names]

  if args.private_network:
    pitr_context.privateNetwork = args.private_network

  if args.preferred_zone:
    pitr_context.preferredZone = args.preferred_zone

  if args.preferred_secondary_zone:
    pitr_context.preferredSecondaryZone = args.preferred_secondary_zone

  if args.allocated_ip_range_name:
    pitr_context.allocatedIpRange = args.allocated_ip_range_name


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA)
class PointInTimeRestore(base.Command):
  """Performs a point in time restore for a Cloud SQL instance managed by Google Cloud Backup and Disaster Recovery."""

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser: parser_extensions.Namespace) -> None:
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use it to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    base.ASYNC_FLAG.AddToParser(parser)
    parser.display_info.AddFormat(flags.GetInstanceListFormat())
    parser.add_argument(
        'datasource',
        help="""\
        The Google Cloud Backup and Disaster Recovery Datasource URI,
        of the form projects/{project}/locations/{region}/backupVaults/
        {backupvault}/dataSources/{datasource}.
        """,
    )
    parser.add_argument(
        'target',
        help='Cloud SQL instance ID of the target instance.',
    )
    parser.add_argument(
        'point_in_time',
        type=arg_parsers.Datetime.Parse,
        help="""\
        The point in time in which to restore the instance to. Uses  RFC 3339
        format in UTC timezone. For example, '2012-11-15T16:19:00.094Z'.
        """,
    )
    parser.add_argument(
        '--private-network',
        required=False,
        help="""\
        The resource link for the VPC network from which the Cloud SQL instance is
        accessible for private IP. For example,
        \'/projects/myProject/global/networks/default\'.
        """,
    )
    parser.add_argument(
        '--allocated-ip-range-name',
        required=False,
        help="""\
        The name of the IP range allocated for the target instance with
        private network connectivity. For example:
        \'google-managed-services-default\'. If set, the target instance
        IP is created in the allocated range represented by this name.
        Reserved for future use.
        """,
    )
    parser.add_argument(
        '--preferred-zone',
        required=False,
        help="""\
        The preferred zone for the target instance. If you specify a value for
        this flag, then the target instance uses the value as the primary
        zone.
        """,
    )
    parser.add_argument(
        '--preferred-secondary-zone',
        required=False,
        help="""\
        The preferred secondary zone for the cloned regional instance. If you
        specify a value for this flag, then the target instance uses the value
        as the secondary zone. The secondary zone can't be the same as the
        primary zone.
        """,
    )
    parser.add_argument(
        '--restore-database-names',
        required=False,
        help="""\
      The name of the databases to be restored for a point-in-time restore. If
      set, the destination instance will only restore the specified databases.
      """,
    )
    flags.AddSourceInstanceOverrideArgs(parser=parser, for_pitr=True)

  def Run(self, args: parser_extensions.Namespace):
    """Performs a point in time restore for a Cloud SQL instance managed by Google Cloud Backup and Disaster Recovery.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A dict object representing if the point-in-time restore operation was
      successful.

    Raises:
      ArgumentError: The arguments are invalid.
    """
    client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
    sql_client = client.sql_client
    sql_messages = client.sql_messages

    specified_args_dict = getattr(args, '_specified_args', None)
    overrides = [
        key
        for key in specified_args_dict
        if key in constants.TARGET_INSTANCE_OVERRIDE_FLAGS
    ]

    request = sql_messages.SqlInstancesPointInTimeRestoreRequest(
        parent=f'projects/{properties.VALUES.core.project.GetOrFail()}',
        pointInTimeRestoreContext=sql_messages.PointInTimeRestoreContext(
            datasource=args.datasource,
            targetInstance=args.target,
            pointInTime=args.point_in_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
        ),
    )
    _UpdateRequestFromArgs(request, args)
    destination_instance_ref = _GetInstanceRefFromArgs(args, client)

    # If the request has overrides, construct the target instance resource from
    # the args and pass it with the request. Note that currently, overrides are
    # only supported for cross project PITR. But here in gcloud, we do not have
    # a way to know whether the PITR is cross project because we do not know the
    # source project. So the check is done in the backend, where if the source
    # and target projects are not different, the overrides will be ignored.
    if overrides:
      instance_resource = (
          command_util.InstancesV1Beta4.ConstructCreateInstanceFromArgs(
              sql_messages, args, instance_ref=destination_instance_ref
          )
      )
      request.pointInTimeRestoreContext.targetInstanceSettings = (
          instance_resource
      )

    response = sql_client.instances.PointInTimeRestore(request)

    operation_ref = client.resource_parser.Create(
        'sql.operations',
        operation=response.name,
        project=destination_instance_ref.project,
    )

    if args.async_:
      if not args.IsSpecified('format'):
        args.format = 'default'
      return sql_client.operations.Get(
          sql_messages.SqlOperationsGetRequest(
              project=operation_ref.project, operation=operation_ref.operation
          )
      )

    operations.OperationsV1Beta4.WaitForOperation(
        sql_client, operation_ref, 'Performing point-in-time restore'
    )
    log.CreatedResource(destination_instance_ref)
    resource = sql_client.instances.Get(
        sql_messages.SqlInstancesGetRequest(
            project=destination_instance_ref.project,
            instance=destination_instance_ref.instance,
        )
    )
    resource.kind = None
    return resource
