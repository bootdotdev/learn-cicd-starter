# -*- coding: utf-8 -*- #
# Copyright 2020 Google LLC. All Rights Reserved.
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
"""Command for creating instances."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import filter_rewrite
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.api_lib.compute.regions import utils as region_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute import scope as compute_scopes
from googlecloudsdk.command_lib.compute.instances import flags as instances_flags
from googlecloudsdk.command_lib.compute.instances.bulk import flags as bulk_flags
from googlecloudsdk.command_lib.compute.instances.bulk import util as bulk_util
from googlecloudsdk.core import log
from googlecloudsdk.core import properties

DETAILED_HELP = {
    'brief': """
          Create multiple Compute Engine virtual machines.
        """,
    'DESCRIPTION': """
        *{command}* facilitates the creation of multiple Compute Engine
        virtual machines with a single command. They offer a number of advantages
        compared to the single instance creation command. This includes the
        ability to automatically pick a zone in which to create instances based
        on resource availability, the ability to specify that the request be
        atomic or best-effort, and a faster rate of instance creation.
        """,
    'EXAMPLES': """
        To create instances called 'example-instance-1', 'example-instance-2',
        and 'example-instance-3' in the 'us-central1-a' zone, run:

          $ {command} --predefined-names=example-instance-1,example-instance-2,example-instance-3 --zone=us-central1-a
        """,
}


def _GetOperations(
    compute_client, project, operation_group_id, holder, location, scope
):
  """Requests operations with group id matching the given one."""

  errors_to_collect = []

  _, operation_filter = filter_rewrite.Rewriter().Rewrite(
      expression='operationGroupId=' + operation_group_id
  )

  resource_parser = holder.resources
  zones = []
  if scope == compute_scopes.ScopeEnum.REGION:
    region_fetcher = region_utils.RegionResourceFetcher(holder.client)
    regions = region_fetcher.GetRegions([
        resource_parser.Create(
            collection='compute.regions', project=project, region=location
        )
    ])
    if len(regions) != 1:
      errors_to_collect.append(
          exceptions.ToolException('Region count is not 1: {}'.format(location))
      )
      return None, errors_to_collect
    zones += [resource_parser.Parse(zone).zone for zone in regions[0].zones]
  else:
    zones += [location]

  operations_response = compute_client.MakeRequests(
      [
          (
              compute_client.apitools_client.zoneOperations,
              'List',
              compute_client.apitools_client.zoneOperations.GetRequestType(
                  'List'
              )(filter=operation_filter, project=project, zone=zone),
          )
          for zone in zones
      ],
      errors_to_collect=errors_to_collect,
      log_result=False,
      always_return_operation=True,
      no_followup=True,
  )

  return operations_response, errors_to_collect


def _GetResult(
    compute_client, request, operation_group_id, holder, location, scope
):
  """Requests operations with group id and parses them as an output."""

  operations_response, errors = _GetOperations(
      compute_client,
      request.project,
      operation_group_id,
      holder,
      location,
      scope,
  )
  if errors:
    utils.RaiseToolException(errors, error_message='Could not fetch resource:')
  result = {'operationGroupId': operation_group_id, 'instances': []}
  successful = [
      op
      for op in operations_response
      if op.operationType == 'insert'
      and str(op.status) == 'DONE'
      and op.error is None
  ]
  num_successful = len(successful)
  num_unsuccessful = request.bulkInsertInstanceResource.count - num_successful

  def GetInstanceStatus(op):
    return {
        'id': op.targetId,
        'name': op.targetLink.split('/')[-1],
        'zone': op.zone,
        'selfLink': op.targetLink,
    }

  instances_status = [GetInstanceStatus(op) for op in successful]

  result['createdInstanceCount'] = num_successful
  result['failedInstanceCount'] = num_unsuccessful
  result['instances'] = instances_status

  return result


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Create(base.Command):
  """Create Compute Engine virtual machine instances."""

  _support_display_device = False
  _support_secure_tags = False
  _support_numa_node_count = False
  _support_snp_svsm = False
  _support_max_count_per_zone = True
  _support_custom_hostnames = False
  _support_specific_then_x_affinity = False
  _support_watchdog_timer = False
  _support_graceful_shutdown = True
  _support_flex_start = False
  _support_source_snapshot_region = False
  _support_skip_guest_os_shutdown = True
  _support_preemption_notice_duration = False

  _log_async = False

  @classmethod
  def Args(cls, parser):
    bulk_flags.AddCommonBulkInsertArgs(
        parser,
        base.ReleaseTrack.GA,
        support_display_device=cls._support_display_device,
        support_numa_node_count=cls._support_numa_node_count,
        support_snp_svsm=cls._support_snp_svsm,
        support_max_count_per_zone=cls._support_max_count_per_zone,
        support_custom_hostnames=cls._support_custom_hostnames,
        support_specific_then_x_affinity=cls._support_specific_then_x_affinity,
        support_watchdog_timer=cls._support_watchdog_timer,
        support_flex_start=cls._support_flex_start,
        support_source_snapshot_region=cls._support_source_snapshot_region,
        support_skip_guest_os_shutdown=cls._support_skip_guest_os_shutdown,
        support_preemption_notice_duration=cls._support_preemption_notice_duration,
    )
    cls.AddSourceInstanceTemplate(parser)

    # Flags specific to GA release track
    instances_flags.AddLocalSsdRecoveryTimeoutArgs(parser)
    instances_flags.AddHostErrorTimeoutSecondsArgs(parser)

  # LINT.IfChange(instance_template)
  @classmethod
  def AddSourceInstanceTemplate(cls, parser):
    cls.SOURCE_INSTANCE_TEMPLATE = (
        bulk_flags.MakeBulkSourceInstanceTemplateArg()
    )
    cls.SOURCE_INSTANCE_TEMPLATE.AddArgument(parser)

  # LINT.ThenChange(../../queued_resources/create.py:instance_template)

  def Collection(self):
    return 'compute.instances'

  def _CreateRequests(
      self,
      args,
      holder,
      compute_client,
      resource_parser,
      project,
      location,
      scope,
  ):
    supported_features = bulk_util.SupportedFeatures(
        self._support_display_device,
        self._support_secure_tags,
        self._support_numa_node_count,
        self._support_snp_svsm,
        self._support_max_count_per_zone,
        self._support_custom_hostnames,
        self._support_specific_then_x_affinity,
        self._support_watchdog_timer,
        self._support_graceful_shutdown,
        self._support_source_snapshot_region,
        self._support_skip_guest_os_shutdown,
        self._support_preemption_notice_duration,
    )
    bulk_instance_resource = bulk_util.CreateBulkInsertInstanceResource(
        args,
        holder,
        compute_client,
        resource_parser,
        project,
        location,
        scope,
        self.SOURCE_INSTANCE_TEMPLATE,
        supported_features,
    )

    if scope == compute_scopes.ScopeEnum.ZONE:
      instance_service = compute_client.apitools_client.instances
      request_message = (
          compute_client.messages.ComputeInstancesBulkInsertRequest(
              bulkInsertInstanceResource=bulk_instance_resource,
              project=project,
              zone=location,
          )
      )
    elif scope == compute_scopes.ScopeEnum.REGION:
      instance_service = compute_client.apitools_client.regionInstances
      request_message = (
          compute_client.messages.ComputeRegionInstancesBulkInsertRequest(
              bulkInsertInstanceResource=bulk_instance_resource,
              project=project,
              region=location,
          )
      )

    return instance_service, request_message

  def Run(self, args):
    """Runs bulk create command.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      A resource object dispatched by display.Displayer().
    """
    bulk_flags.ValidateBulkInsertArgs(
        args,
        support_max_count_per_zone=self._support_max_count_per_zone,
        support_custom_hostnames=self._support_custom_hostnames,
    )

    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    compute_client = holder.client
    resource_parser = holder.resources

    project = properties.VALUES.core.project.GetOrFail()
    location = None
    scope = None

    if args.IsSpecified('zone'):
      location = args.zone
      scope = compute_scopes.ScopeEnum.ZONE
    elif args.IsSpecified('region'):
      location = args.region
      scope = compute_scopes.ScopeEnum.REGION

    instances_service, request = self._CreateRequests(
        args, holder, compute_client, resource_parser, project, location, scope
    )

    self._errors = []
    self._log_async = False
    self._status_message = None

    if args.async_:
      self._log_async = True
      try:
        response = instances_service.BulkInsert(request)
        self._operation_selflink = response.selfLink
        return {'operationGroupId': response.operationGroupId}
      except exceptions.HttpException as error:
        raise error

    response = compute_client.MakeRequests(
        [(instances_service, 'BulkInsert', request)],
        log_result=False,
        always_return_operation=True,
        no_followup=True,
    )

    self._errors = []
    if response:
      operation_group_id = response[0].operationGroupId
      result = _GetResult(
          compute_client, request, operation_group_id, holder, location, scope
      )
      if (
          result.get('createdInstanceCount') is not None
          and result.get('failedInstanceCount') is not None
      ):
        self._status_message = 'VM instances created: {}, failed: {}.'.format(
            result['createdInstanceCount'], result['failedInstanceCount']
        )
      return result
    return

  def Epilog(self, resources_were_displayed):
    del resources_were_displayed
    if self._errors:
      for error in self._errors:
        log.error(error[1])
    elif self._log_async:
      log.status.Print(
          'Bulk instance creation in progress: {}'.format(
              self._operation_selflink
          )
      )
    else:
      if self._errors:
        for error in self._errors:
          log.warning(error[1])
      log.status.Print(
          'Bulk create request finished with status message: [{}]'.format(
              self._status_message
          )
      )


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateBeta(Create):
  """Create Compute Engine virtual machine instances."""

  _support_display_device = True
  _support_secure_tags = False
  _support_numa_node_count = False
  _support_snp_svsm = False
  _support_max_count_per_zone = True
  _support_custom_hostnames = True
  _support_specific_then_x_affinity = True
  _support_watchdog_timer = False
  _support_graceful_shutdown = True
  _support_flex_start = False
  _support_igmp_query = False
  _support_source_snapshot_region = False
  _support_skip_guest_os_shutdown = True
  _support_preemption_notice_duration = False

  @classmethod
  def Args(cls, parser):
    bulk_flags.AddCommonBulkInsertArgs(
        parser,
        base.ReleaseTrack.BETA,
        support_display_device=cls._support_display_device,
        support_numa_node_count=cls._support_numa_node_count,
        support_snp_svsm=cls._support_snp_svsm,
        support_max_count_per_zone=cls._support_max_count_per_zone,
        support_custom_hostnames=cls._support_custom_hostnames,
        support_specific_then_x_affinity=cls._support_specific_then_x_affinity,
        support_watchdog_timer=cls._support_watchdog_timer,
        support_graceful_shutdown=cls._support_graceful_shutdown,
        support_flex_start=cls._support_flex_start,
        support_igmp_query=cls._support_igmp_query,
        support_source_snapshot_region=cls._support_source_snapshot_region,
        support_skip_guest_os_shutdown=cls._support_skip_guest_os_shutdown,
        support_preemption_notice_duration=cls._support_preemption_notice_duration,
    )
    cls.AddSourceInstanceTemplate(parser)

    # Flags specific to Beta release track
    instances_flags.AddHostErrorTimeoutSecondsArgs(parser)
    instances_flags.AddLocalSsdRecoveryTimeoutArgs(parser)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateAlpha(Create):
  """Create Compute Engine virtual machine instances."""

  # LINT.IfChange(alpha_spec)
  _support_display_device = True
  _support_secure_tags = True
  _support_numa_node_count = True
  _support_snp_svsm = True
  _support_max_count_per_zone = True
  _support_custom_hostnames = True
  _support_specific_then_x_affinity = True
  _support_watchdog_timer = True
  _support_igmp_query = True
  _support_graceful_shutdown = True
  _support_flex_start = False
  _support_source_snapshot_region = True
  _support_skip_guest_os_shutdown = True
  _support_preemption_notice_duration = True

  @classmethod
  def Args(cls, parser):
    bulk_flags.AddCommonBulkInsertArgs(
        parser,
        base.ReleaseTrack.ALPHA,
        support_display_device=cls._support_display_device,
        support_numa_node_count=cls._support_numa_node_count,
        support_snp_svsm=cls._support_snp_svsm,
        support_max_count_per_zone=cls._support_max_count_per_zone,
        support_custom_hostnames=cls._support_custom_hostnames,
        support_specific_then_x_affinity=cls._support_specific_then_x_affinity,
        support_watchdog_timer=cls._support_watchdog_timer,
        support_igmp_query=cls._support_igmp_query,
        support_graceful_shutdown=cls._support_graceful_shutdown,
        support_flex_start=cls._support_flex_start,
        support_source_snapshot_region=cls._support_source_snapshot_region,
        support_skip_guest_os_shutdown=cls._support_skip_guest_os_shutdown,
        support_preemption_notice_duration=cls._support_preemption_notice_duration,
    )

    cls.AddSourceInstanceTemplate(parser)

    # Flags specific to Alpha release track
    instances_flags.AddSecureTagsArgs(parser)
    instances_flags.AddHostErrorTimeoutSecondsArgs(parser)
    instances_flags.AddMaintenanceInterval().AddToParser(parser)
    instances_flags.AddLocalSsdRecoveryTimeoutArgs(parser)

  # LINT.ThenChange(../../queued_resources/create.py:alpha_spec)


Create.detailed_help = DETAILED_HELP
