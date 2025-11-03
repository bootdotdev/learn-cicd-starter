# -*- coding: utf-8 -*- #
# Copyright 2014 Google LLC. All Rights Reserved.
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

"""Command for adding a backend to a backend service."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import encoding

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import exceptions
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.backend_services import backend_flags
from googlecloudsdk.command_lib.compute.backend_services import backend_services_utils
from googlecloudsdk.command_lib.compute.backend_services import flags


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class AddBackend(base.UpdateCommand):
  """Add a backend to a backend service.

  *{command}* adds a backend to a Google Cloud load balancer or Traffic
  Director. Depending on the load balancing scheme of the backend service,
  backends can be instance groups (managed or unmanaged), zonal network endpoint
  groups (zonal NEGs), serverless NEGs, or an internet NEG. For more
  information, see the [backend services
  overview](https://cloud.google.com/load-balancing/docs/backend-service).

  For most load balancers, you can define how Google Cloud measures capacity by
  selecting a balancing mode. For more information, see [traffic
  distribution](https://cloud.google.com/load-balancing/docs/backend-service#traffic_distribution).

  To modify a backend, use the `gcloud compute backend-services update-backend`
  or `gcloud compute backend-services edit` command.
  """

  support_global_neg = True
  support_region_neg = True
  support_failover = True
  support_in_flight_balancing = False

  @classmethod
  def Args(cls, parser):
    flags.GLOBAL_REGIONAL_BACKEND_SERVICE_ARG.AddArgument(parser)
    backend_flags.AddDescription(parser)
    flags.AddInstanceGroupAndNetworkEndpointGroupArgs(
        parser,
        'add to',
        support_global_neg=cls.support_global_neg,
        support_region_neg=cls.support_region_neg)
    backend_flags.AddBalancingMode(
        parser,
        support_global_neg=cls.support_global_neg,
        support_region_neg=cls.support_region_neg,
        release_track=cls.ReleaseTrack(),
    )
    backend_flags.AddCapacityLimits(
        parser,
        support_global_neg=cls.support_global_neg,
        support_region_neg=cls.support_region_neg,
        release_track=cls.ReleaseTrack(),
    )
    backend_flags.AddCapacityScalar(
        parser,
        support_global_neg=cls.support_global_neg,
        support_region_neg=cls.support_region_neg,
    )
    backend_flags.AddPreference(parser)
    if cls.support_failover:
      backend_flags.AddFailover(parser, default=None)
    if cls.support_in_flight_balancing:
      backend_flags.AddTrafficDuration(parser)
    backend_flags.AddCustomMetrics(parser)

  def _GetGetRequest(self, client, backend_service_ref):
    if backend_service_ref.Collection() == 'compute.regionBackendServices':
      return (client.apitools_client.regionBackendServices,
              'Get',
              client.messages.ComputeRegionBackendServicesGetRequest(
                  backendService=backend_service_ref.Name(),
                  region=backend_service_ref.region,
                  project=backend_service_ref.project))
    return (client.apitools_client.backendServices,
            'Get',
            client.messages.ComputeBackendServicesGetRequest(
                backendService=backend_service_ref.Name(),
                project=backend_service_ref.project))

  def _GetSetRequest(self, client, backend_service_ref, replacement):
    if backend_service_ref.Collection() == 'compute.regionBackendServices':
      return (client.apitools_client.regionBackendServices,
              'Update',
              client.messages.ComputeRegionBackendServicesUpdateRequest(
                  backendService=backend_service_ref.Name(),
                  backendServiceResource=replacement,
                  region=backend_service_ref.region,
                  project=backend_service_ref.project))
    return (client.apitools_client.backendServices,
            'Update',
            client.messages.ComputeBackendServicesUpdateRequest(
                backendService=backend_service_ref.Name(),
                backendServiceResource=replacement,
                project=backend_service_ref.project))

  def _GetGroupRef(self, args, resources, client):
    if args.instance_group:
      return flags.MULTISCOPE_INSTANCE_GROUP_ARG.ResolveAsResource(
          args,
          resources,
          scope_lister=compute_flags.GetDefaultScopeLister(client))
    if args.network_endpoint_group:
      return flags.GetNetworkEndpointGroupArg(
          support_global_neg=self.support_global_neg,
          support_region_neg=self.support_region_neg).ResolveAsResource(
              args,
              resources,
              scope_lister=compute_flags.GetDefaultScopeLister(client))

  def _CreateBackendMessage(
      self,
      messages,
      group_uri,
      balancing_mode,
      preference,
      traffic_duration,
      args,
  ):
    """Create a backend message.

    Args:
      messages: The available API proto messages.
      group_uri: String. The backend instance group uri.
      balancing_mode: Backend.BalancingModeValueValuesEnum. The backend load
        balancing mode.
      preference: Backend.PreferenceValueValuesEnum. The backend preference
      traffic_duration: Backend.TrafficDurationValueValuesEnum. The traffic
        duration for the backend.
      args: argparse Namespace. The arguments given to the add-backend command.

    Returns:
      A new Backend message with its fields set according to the given
      arguments.
    """
    backend_services_utils.ValidateBalancingModeArgs(
        messages, args, self.ReleaseTrack()
    )
    if preference is not None:
      backend = messages.Backend(
          balancingMode=balancing_mode,
          preference=preference,
          capacityScaler=args.capacity_scaler,
          description=args.description,
          group=group_uri,
          maxRate=args.max_rate,
          maxRatePerInstance=args.max_rate_per_instance,
          maxRatePerEndpoint=args.max_rate_per_endpoint,
          maxUtilization=args.max_utilization,
          maxConnections=args.max_connections,
          maxConnectionsPerInstance=args.max_connections_per_instance,
          maxConnectionsPerEndpoint=args.max_connections_per_endpoint,
          failover=args.failover,
      )
      if (
          self.ReleaseTrack() == base.ReleaseTrack.ALPHA
          or self.ReleaseTrack() == base.ReleaseTrack.BETA
      ):
        backend.maxInFlightRequests = args.max_in_flight_requests
        backend.maxInFlightRequestsPerInstance = (
            args.max_in_flight_requests_per_instance
        )
        backend.maxInFlightRequestsPerEndpoint = (
            args.max_in_flight_requests_per_endpoint
        )
        backend.trafficDuration = traffic_duration

      return backend
    else:
      backend = messages.Backend(
          balancingMode=balancing_mode,
          capacityScaler=args.capacity_scaler,
          description=args.description,
          group=group_uri,
          maxRate=args.max_rate,
          maxRatePerInstance=args.max_rate_per_instance,
          maxRatePerEndpoint=args.max_rate_per_endpoint,
          maxUtilization=args.max_utilization,
          maxConnections=args.max_connections,
          maxConnectionsPerInstance=args.max_connections_per_instance,
          maxConnectionsPerEndpoint=args.max_connections_per_endpoint,
          failover=args.failover,
      )
      if (
          self.ReleaseTrack() == base.ReleaseTrack.ALPHA
          or self.ReleaseTrack() == base.ReleaseTrack.BETA
      ):
        backend.maxInFlightRequests = args.max_in_flight_requests
        backend.maxInFlightRequestsPerInstance = (
            args.max_in_flight_requests_per_instance
        )
        backend.maxInFlightRequestsPerEndpoint = (
            args.max_in_flight_requests_per_endpoint
        )
        backend.trafficDuration = traffic_duration

      return backend

  def _Modify(self, client, resources, backend_service_ref, args, existing):
    replacement = encoding.CopyProtoMessage(existing)

    group_ref = self._GetGroupRef(args, resources, client)
    group_uri = group_ref.SelfLink()

    scope = ''
    for backend in existing.backends:
      if group_uri == backend.group:
        if (
            group_ref.Collection() == 'compute.instanceGroups'
            or group_ref.Collection() == 'compute.networkEndpointGroups'
        ):
          scope = 'zone [' + getattr(group_ref, 'zone') + ']'
        elif (
            group_ref.Collection() == 'compute.regionInstanceGroups'
            or group_ref.Collection() == 'compute.regionNetworkEndpointGroups'
        ):
          scope = 'region [' + getattr(group_ref, 'region') + ']'
        elif group_ref.Collection() == 'compute.globalNetworkEndpointGroups':
          scope = 'global'

        raise exceptions.ArgumentError(
            'Backend [{}] in {} already exists in backend service [{}].'.format(
                group_ref.Name(), scope, backend_service_ref.Name()
            )
        )

    if args.balancing_mode:
      balancing_mode = client.messages.Backend.BalancingModeValueValuesEnum(
          args.balancing_mode)
    else:
      balancing_mode = None

    preference = None
    if args.preference:
      preference = client.messages.Backend.PreferenceValueValuesEnum(
          args.preference)

    traffic_duration = None
    if (
        self.ReleaseTrack() == base.ReleaseTrack.ALPHA
        or self.ReleaseTrack() == base.ReleaseTrack.BETA
    ) and args.traffic_duration:
      traffic_duration = client.messages.Backend.TrafficDurationValueValuesEnum(
          args.traffic_duration
      )

    backend = self._CreateBackendMessage(
        client.messages,
        group_uri,
        balancing_mode,
        preference,
        traffic_duration,
        args,
    )
    if args.custom_metrics:
      backend.customMetrics = args.custom_metrics
    if args.custom_metrics_file:
      backend.customMetrics = args.custom_metrics_file

    replacement.backends.append(backend)
    return replacement

  def Run(self, args):
    """Issues requests necessary to add backend to the Backend Service."""
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    backend_service_ref = (
        flags.GLOBAL_REGIONAL_BACKEND_SERVICE_ARG.ResolveAsResource(
            args,
            holder.resources,
            scope_lister=compute_flags.GetDefaultScopeLister(client)))
    get_request = self._GetGetRequest(client, backend_service_ref)

    objects = client.MakeRequests([get_request])

    new_object = self._Modify(client, holder.resources, backend_service_ref,
                              args, objects[0])

    return client.MakeRequests(
        [self._GetSetRequest(client, backend_service_ref, new_object)])


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class AddBackendBeta(AddBackend):
  """Add a backend to a backend service.

  *{command}* adds a backend to a Google Cloud load balancer or Traffic
  Director. Depending on the load balancing scheme of the backend service,
  backends can be instance groups (managed or unmanaged), zonal network endpoint
  groups (zonal NEGs), serverless NEGs, or an internet NEG. For more
  information, see the [backend services
  overview](https://cloud.google.com/load-balancing/docs/backend-service).

  For most load balancers, you can define how Google Cloud measures capacity by
  selecting a balancing mode. For more information, see [traffic
  distribution](https://cloud.google.com/load-balancing/docs/backend-service#traffic_distribution).

  To modify a backend, use the `gcloud compute backend-services update-backend`
  or `gcloud compute backend-services edit` command.
  """

  # Allow --preference flag to be set when updating the backend.
  support_in_flight_balancing = True


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AddBackendAlpha(AddBackend):
  """Add a backend to a backend service.

  *{command}* adds a backend to a Google Cloud load balancer or Traffic
  Director. Depending on the load balancing scheme of the backend service,
  backends can be instance groups (managed or unmanaged), zonal network endpoint
  groups (zonal NEGs), serverless NEGs, or an internet NEG. For more
  information, see the [backend services
  overview](https://cloud.google.com/load-balancing/docs/backend-service).

  For most load balancers, you can define how Google Cloud measures capacity by
  selecting a balancing mode. For more information, see [traffic
  distribution](https://cloud.google.com/load-balancing/docs/backend-service#traffic_distribution).

  To modify a backend, use the `gcloud compute backend-services update-backend`
  or `gcloud compute backend-services edit` command.
  """
  # Allow --preference flag to be set when updating the backend.
  support_in_flight_balancing = True
