# -*- coding: utf-8 -*- #
# Copyright 2022 Google LLC. All Rights Reserved.
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
"""Command for creating machine images."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import uuid

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scopes
from googlecloudsdk.command_lib.compute.instances import flags as instances_flags
from googlecloudsdk.command_lib.compute.instances.bulk import flags as bulk_flags
from googlecloudsdk.command_lib.compute.instances.bulk import util as bulk_util
from googlecloudsdk.command_lib.compute.queued_resources import flags as queued_resource_flags
from googlecloudsdk.core import log


@base.UniverseCompatible
class Create(base.CreateCommand):
  """Create a Compute Engine queued resource."""

  _ALLOW_RSA_ENCRYPTED_CSEK_KEYS = True

  detailed_help = {
      'brief': 'Create a Compute Engine queued resource.',
      'EXAMPLES': """
     To create a queued resource, run:

       $ {command} queued-resource-1 --count=1 --name-pattern=instance-#
         --valid-until-duration=7d --zone=us-central1-a
   """,
  }
  # LINT.IfChange(alpha_spec)
  _support_display_device = True
  _support_secure_tags = True
  _support_numa_node_count = True
  _support_snp_svsm = True
  _support_max_count_per_zone = False
  _support_custom_hostnames = True
  _support_specific_then_x = True
  _support_watchdog_timer = True
  _support_igmp_query = True
  _support_graceful_shutdown = True
  _support_flex_start = True
  _support_source_snapshot_region = True
  _support_skip_guest_os_shutdown = True
  _support_preemption_notice_duration = True

  @classmethod
  def Args(cls, parser):
    # Bulk insert specific flags
    bulk_flags.AddCommonBulkInsertArgs(
        parser,
        base.ReleaseTrack.ALPHA,
        support_display_device=cls._support_display_device,
        support_numa_node_count=cls._support_numa_node_count,
        add_zone_region_flags=False,
        support_snp_svsm=cls._support_snp_svsm,
        support_max_count_per_zone=cls._support_max_count_per_zone,
        support_custom_hostnames=cls._support_custom_hostnames,
        support_specific_then_x_affinity=cls._support_specific_then_x,
        support_watchdog_timer=cls._support_watchdog_timer,
        support_igmp_query=cls._support_igmp_query,
        support_graceful_shutdown=cls._support_graceful_shutdown,
        support_flex_start=cls._support_flex_start,
        support_source_snapshot_region=cls._support_source_snapshot_region,
        support_skip_guest_os_shutdown=cls._support_skip_guest_os_shutdown,
        support_preemption_notice_duration=cls._support_preemption_notice_duration,
    )
    cls.AddSourceInstanceTemplate(parser)
    instances_flags.AddSecureTagsArgs(parser)
    instances_flags.AddHostErrorTimeoutSecondsArgs(parser)
    instances_flags.AddLocalSsdRecoveryTimeoutArgs(parser)
    instances_flags.AddMaintenanceInterval().AddToParser(parser)
    # LINT.ThenChange(../instances/bulk/create.py:alpha_spec)
    # Queued resource specific flags
    valid_until_group = parser.add_group(mutex=True, required=True)
    valid_until_group.add_argument(
        '--valid-until-duration',
        type=arg_parsers.Duration(),
        help="""Relative deadline for waiting for capacity.""",
    )
    valid_until_group.add_argument(
        '--valid-until-time',
        type=arg_parsers.Datetime.Parse,
        help="""Absolute deadline for waiting for capacity in RFC3339 text format.""",
    )
    Create.QueuedResourceArg = queued_resource_flags.MakeQueuedResourcesArg(
        plural=False
    )
    Create.QueuedResourceArg.AddArgument(parser, operation_type='create')
    queued_resource_flags.AddOutputFormat(parser)

  # LINT.IfChange(instance_template)
  @classmethod
  def AddSourceInstanceTemplate(cls, parser):
    cls.SOURCE_INSTANCE_TEMPLATE = (
        bulk_flags.MakeBulkSourceInstanceTemplateArg()
    )
    cls.SOURCE_INSTANCE_TEMPLATE.AddArgument(parser)

  # LINT.ThenChange(../instances/bulk/create.py:instance_template)

  def Run(self, args):
    bulk_flags.ValidateBulkInsertArgs(
        args,
        support_max_count_per_zone=self._support_max_count_per_zone,
        support_custom_hostnames=self._support_custom_hostnames,
    )

    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    queued_resource_ref = Create.QueuedResourceArg.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
    )

    zone = args.zone
    if not zone and queued_resource_ref.zone:
      zone = queued_resource_ref.zone

    supported_features = bulk_util.SupportedFeatures(
        self._support_display_device,
        self._support_secure_tags,
        self._support_numa_node_count,
        self._support_snp_svsm,
        self._support_max_count_per_zone,
        self._support_custom_hostnames,
        self._support_specific_then_x,
        self._support_watchdog_timer,
        self._support_graceful_shutdown,
        self._support_source_snapshot_region,
        self._support_skip_guest_os_shutdown,
        self._support_preemption_notice_duration,
    )
    bulk_insert_instance_resource = bulk_util.CreateBulkInsertInstanceResource(
        args,
        holder,
        client,
        holder.resources,
        queued_resource_ref.project,
        zone,
        compute_scopes.ScopeEnum.ZONE,
        self.SOURCE_INSTANCE_TEMPLATE,
        supported_features,
    )

    # minCount is not supported in QueuedResource
    bulk_insert_instance_resource.reset('minCount')

    queued_resource = client.messages.QueuedResource(
        name=queued_resource_ref.Name(),
        queuingPolicy=client.messages.QueuingPolicy(
            validUntilDuration=client.messages.Duration(
                seconds=args.valid_until_duration
            )
        ),
        bulkInsertInstanceResource=bulk_insert_instance_resource,
    )

    request = client.messages.ComputeZoneQueuedResourcesInsertRequest(
        queuedResource=queued_resource,
        project=queued_resource_ref.project,
        zone=queued_resource_ref.zone,
        requestId=str(uuid.uuid4()),
    )
    if args.async_:
      response = client.apitools_client.zoneQueuedResources.Insert(request)
      log.status.Print(
          'Queued resource creation in progress: {}'.format(response.selfLink)
      )
      # Disable argument formatting since we have not created a resource yet.
      args.format = 'disable'
      return response
    return client.MakeRequests(
        [(client.apitools_client.zoneQueuedResources, 'Insert', request)]
    )
