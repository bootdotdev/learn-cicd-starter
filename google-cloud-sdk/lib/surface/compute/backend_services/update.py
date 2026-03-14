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
"""Commands for updating backend services.

   There are separate alpha, beta, and GA command classes in this file.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import encoding

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.backend_services import (
    client as backend_service_client)
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute import cdn_flags_utils as cdn_flags
from googlecloudsdk.command_lib.compute import exceptions as compute_exceptions
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import reference_utils
from googlecloudsdk.command_lib.compute import signed_url_flags
from googlecloudsdk.command_lib.compute.backend_services import backend_services_utils
from googlecloudsdk.command_lib.compute.backend_services import flags
from googlecloudsdk.command_lib.compute.security_policies import (
    flags as security_policy_flags)
from googlecloudsdk.core import log


def AddIapFlag(parser):
  # TODO(b/34479878): It would be nice if the auto-generated help text were
  # a bit better so we didn't need to be quite so verbose here.
  flags.AddIap(
      parser,
      help="""\
      Change the Identity Aware Proxy (IAP) service configuration for the
      backend service. You can set IAP to 'enabled' or 'disabled', or modify
      the OAuth2 client configuration (oauth2-client-id and
      oauth2-client-secret) used by IAP. If any fields are unspecified, their
      values will not be modified. For instance, if IAP is enabled,
      '--iap=disabled' will disable IAP, and a subsequent '--iap=enabled' will
      then enable it with the same OAuth2 client configuration as the first
      time it was enabled. See
      https://cloud.google.com/iap/ for more information about this feature.
      """)


class UpdateHelper(object):
  """Helper class that updates a backend service."""

  HEALTH_CHECK_ARG = None
  HTTP_HEALTH_CHECK_ARG = None
  HTTPS_HEALTH_CHECK_ARG = None
  SECURITY_POLICY_ARG = None
  EDGE_SECURITY_POLICY_ARG = None

  @classmethod
  def Args(
      cls,
      parser,
      support_subsetting_subset_size,
      support_ip_port_dynamic_forwarding,
      support_zonal_affinity,
      support_allow_multinetwork,
  ):
    """Add all arguments for updating a backend service."""

    flags.GLOBAL_REGIONAL_BACKEND_SERVICE_ARG.AddArgument(
        parser, operation_type='update')
    flags.AddDescription(parser)
    cls.HEALTH_CHECK_ARG = flags.HealthCheckArgument()
    cls.HEALTH_CHECK_ARG.AddArgument(parser, cust_metavar='HEALTH_CHECK')
    cls.HTTP_HEALTH_CHECK_ARG = flags.HttpHealthCheckArgument()
    cls.HTTP_HEALTH_CHECK_ARG.AddArgument(
        parser, cust_metavar='HTTP_HEALTH_CHECK')
    cls.HTTPS_HEALTH_CHECK_ARG = flags.HttpsHealthCheckArgument()
    cls.HTTPS_HEALTH_CHECK_ARG.AddArgument(
        parser, cust_metavar='HTTPS_HEALTH_CHECK')
    flags.AddNoHealthChecks(parser)
    cls.SECURITY_POLICY_ARG = (
        security_policy_flags
        .SecurityPolicyMultiScopeArgumentForTargetResource(
            resource='backend service',
            region_hidden=True,
            scope_flags_usage=compute_flags.ScopeFlagsUsage
            .USE_EXISTING_SCOPE_FLAGS,
            short_help_text=(
                'The security policy that will be set for this {0}.')))
    cls.SECURITY_POLICY_ARG.AddArgument(parser)
    cls.EDGE_SECURITY_POLICY_ARG = (
        security_policy_flags.EdgeSecurityPolicyArgumentForTargetResource(
            resource='backend service'))
    cls.EDGE_SECURITY_POLICY_ARG.AddArgument(parser)
    flags.AddTimeout(parser, default=None)
    flags.AddPortName(parser)
    flags.AddProtocol(parser, default=None)

    flags.AddConnectionDrainingTimeout(parser)
    flags.AddEnableCdn(parser)
    flags.AddCacheKeyIncludeProtocol(parser, default=None)
    flags.AddCacheKeyIncludeHost(parser, default=None)
    flags.AddCacheKeyIncludeQueryString(parser, default=None)
    flags.AddCacheKeyQueryStringList(parser)
    flags.AddCacheKeyExtendedCachingArgs(parser)
    flags.AddSessionAffinity(
        parser,
        support_stateful_affinity=True,
    )
    flags.AddAffinityCookie(parser, support_stateful_affinity=True)
    signed_url_flags.AddSignedUrlCacheMaxAge(
        parser, required=False, unspecified_help='')
    flags.AddSubsettingPolicy(parser)
    if support_subsetting_subset_size:
      flags.AddSubsettingSubsetSize(parser)

    flags.AddConnectionDrainOnFailover(parser, default=None)
    flags.AddDropTrafficIfUnhealthy(parser, default=None)
    flags.AddFailoverRatio(parser)
    flags.AddEnableLogging(parser)
    flags.AddLoggingSampleRate(parser)
    flags.AddLoggingOptional(parser)
    flags.AddLoggingOptionalFields(parser)

    AddIapFlag(parser)
    flags.AddCustomRequestHeaders(parser, remove_all_flag=True, default=None)

    cdn_flags.AddCdnPolicyArgs(parser, 'backend service', update_command=True)

    flags.AddConnectionTrackingPolicy(parser)
    flags.AddCompressionMode(parser)

    flags.AddServiceLoadBalancingPolicy(parser, required=False, is_update=True)

    flags.AddServiceBindings(parser, required=False, is_update=True)
    flags.AddLocalityLbPolicy(parser, is_update=True)
    flags.AddIpAddressSelectionPolicy(parser)
    flags.AddExternalMigration(parser)

    flags.AddBackendServiceTlsSettings(parser, add_clear_argument=True)
    flags.AddBackendServiceCustomMetrics(parser, add_clear_argument=True)
    if support_ip_port_dynamic_forwarding:
      flags.AddIpPortDynamicForwarding(parser)
    if support_zonal_affinity:
      flags.AddZonalAffinity(parser)
    if support_allow_multinetwork:
      flags.AddAllowMultinetwork(parser)

  def __init__(
      self,
      support_subsetting_subset_size,
      support_ip_port_dynamic_forwarding=False,
      support_zonal_affinity=False,
      support_allow_multinetwork=False,
      release_track=None,
  ):
    self._support_subsetting_subset_size = support_subsetting_subset_size
    self._support_ip_port_dynamic_forwarding = (
        support_ip_port_dynamic_forwarding
    )
    self._support_zonal_affinity = support_zonal_affinity
    self._support_allow_multinetwork = support_allow_multinetwork
    self._release_track = release_track

  def Modify(self, client, resources, args, existing, backend_service_ref):
    """Modify Backend Service."""
    replacement = encoding.CopyProtoMessage(existing)
    cleared_fields = []
    location = (
        backend_service_ref.region if backend_service_ref.Collection()
        == 'compute.regionBackendServices' else 'global')

    if args.connection_draining_timeout is not None:
      replacement.connectionDraining = client.messages.ConnectionDraining(
          drainingTimeoutSec=args.connection_draining_timeout)
    if args.no_custom_request_headers is not None:
      replacement.customRequestHeaders = []
    if args.custom_request_header is not None:
      replacement.customRequestHeaders = args.custom_request_header
    if not replacement.customRequestHeaders:
      cleared_fields.append('customRequestHeaders')

    if args.custom_response_header is not None:
      replacement.customResponseHeaders = args.custom_response_header
    if args.no_custom_response_headers:
      replacement.customResponseHeaders = []
    if not replacement.customResponseHeaders:
      cleared_fields.append('customResponseHeaders')

    if args.IsSpecified('description'):
      replacement.description = args.description

    health_checks = flags.GetHealthCheckUris(args, self, resources)
    if health_checks:
      replacement.healthChecks = health_checks

    if args.IsSpecified('no_health_checks'):
      replacement.healthChecks = []
      cleared_fields.append('healthChecks')

    if args.timeout:
      replacement.timeoutSec = args.timeout

    if args.port_name:
      replacement.portName = args.port_name

    if args.protocol:
      replacement.protocol = (
          client.messages.BackendService.ProtocolValueValuesEnum(args.protocol))

    if args.enable_cdn is not None:
      replacement.enableCDN = args.enable_cdn
    elif not replacement.enableCDN and args.cache_mode:
      # TODO(b/209812994): Replace implicit config change with
      # warning that CDN is disabled and a prompt to enable it with
      # --enable-cdn
      log.warning(
          'Setting a cache mode also enabled Cloud CDN, which was previously ' +
          'disabled. If this was not intended, disable Cloud ' +
          'CDN with `--no-enable-cdn`.')
      replacement.enableCDN = True

    if args.session_affinity is not None:
      replacement.sessionAffinity = (
          client.messages.BackendService.SessionAffinityValueValuesEnum(
              args.session_affinity))
      # strongSessionAffinityCookie only usable with STRONG_COOKIE_AFFINITY.
      if args.session_affinity != 'STRONG_COOKIE_AFFINITY':
        cleared_fields.append('strongSessionAffinityCookie')

    backend_services_utils.ApplyAffinityCookieArgs(client, args, replacement)

    if args.connection_draining_timeout is not None:
      replacement.connectionDraining = client.messages.ConnectionDraining(
          drainingTimeoutSec=args.connection_draining_timeout)

    backend_services_utils.ApplySubsettingArgs(
        client, args, replacement, self._support_subsetting_subset_size
    )

    if args.locality_lb_policy is not None:
      replacement.localityLbPolicy = (
          client.messages.BackendService.LocalityLbPolicyValueValuesEnum(
              args.locality_lb_policy))
    if args.no_locality_lb_policy is not None:
      replacement.localityLbPolicy = None
      cleared_fields.append('localityLbPolicy')

    backend_services_utils.ApplyCdnPolicyArgs(
        client,
        args,
        replacement,
        is_update=True,
        apply_signed_url_cache_max_age=True,
        cleared_fields=cleared_fields)

    backend_services_utils.ApplyConnectionTrackingPolicyArgs(
        client, args, replacement)

    if args.compression_mode is not None:
      replacement.compressionMode = (
          client.messages.BackendService.CompressionModeValueValuesEnum(
              args.compression_mode))

    self._ApplyIapArgs(client, args.iap, existing, replacement)

    backend_services_utils.ApplyFailoverPolicyArgs(
        client.messages, args, replacement
    )

    backend_services_utils.ApplyLogConfigArgs(
        client.messages,
        args,
        replacement,
        cleared_fields=cleared_fields,
    )

    if args.service_lb_policy is not None:
      replacement.serviceLbPolicy = reference_utils.BuildServiceLbPolicyUrl(
          project_name=backend_service_ref.project,
          location=location,
          policy_name=args.service_lb_policy,
          release_track=self._release_track,
      )
    if args.no_service_lb_policy is not None:
      replacement.serviceLbPolicy = None
      cleared_fields.append('serviceLbPolicy')

    if args.service_bindings is not None:
      replacement.serviceBindings = [
          reference_utils.BuildServiceBindingUrl(backend_service_ref.project,
                                                 location, binding_name)
          for binding_name in args.service_bindings
      ]
    if args.no_service_bindings is not None:
      replacement.serviceBindings = []
      cleared_fields.append('serviceBindings')

    backend_services_utils.ApplyIpAddressSelectionPolicyArgs(
        client, args, replacement
    )
    if args.external_managed_migration_state is not None:
      replacement.externalManagedMigrationState = client.messages.BackendService.ExternalManagedMigrationStateValueValuesEnum(
          args.external_managed_migration_state
      )
    if args.external_managed_migration_testing_percentage is not None:
      replacement.externalManagedMigrationTestingPercentage = (
          args.external_managed_migration_testing_percentage
      )
    if args.clear_external_managed_migration_state is not None:
      replacement.externalManagedMigrationState = None
      replacement.externalManagedMigrationTestingPercentage = None
      cleared_fields.append('externalManagedMigrationState')
      cleared_fields.append('externalManagedMigrationTestingPercentage')
    if args.load_balancing_scheme is not None:
      replacement.loadBalancingScheme = (
          client.messages.BackendService.LoadBalancingSchemeValueValuesEnum(
              args.load_balancing_scheme
          )
      )
    if args.tls_settings is not None:
      backend_services_utils.ApplyTlsSettingsArgs(
          client,
          args,
          replacement,
          backend_service_ref.project,
          location,
          self._release_track,
      )
    if args.no_tls_settings is not None:
      replacement.tlsSettings = None
      cleared_fields.append('tlsSettings')
    if args.custom_metrics:
      replacement.customMetrics = args.custom_metrics
    if args.custom_metrics_file:
      replacement.customMetrics = args.custom_metrics_file
    if args.clear_custom_metrics:
      replacement.customMetrics = []
      cleared_fields.append('customMetrics')
    if self._support_ip_port_dynamic_forwarding:
      backend_services_utils.IpPortDynamicForwarding(client, args, replacement)
    if self._support_zonal_affinity:
      backend_services_utils.ZonalAffinity(client, args, replacement)
    if self._support_allow_multinetwork and args.IsSpecified(
        'allow_multinetwork'
    ):
      replacement.allowMultinetwork = args.allow_multinetwork
    return replacement, cleared_fields

  def ValidateArgs(self, args):
    """Validate arguments."""
    if not any([
        args.IsSpecified('affinity_cookie_ttl'),
        args.IsSpecified('connection_draining_timeout'),
        args.IsSpecified('no_custom_request_headers'),
        args.IsSpecified('custom_request_header'),
        args.IsSpecified('description'),
        args.IsSpecified('enable_cdn'),
        args.IsSpecified('cache_key_include_protocol'),
        args.IsSpecified('cache_key_include_host'),
        args.IsSpecified('cache_key_include_query_string'),
        args.IsSpecified('cache_key_query_string_whitelist'),
        args.IsSpecified('cache_key_query_string_blacklist'),
        args.IsSpecified('cache_key_include_http_header'),
        args.IsSpecified('cache_key_include_named_cookie'),
        args.IsSpecified('signed_url_cache_max_age'),
        args.IsSpecified('http_health_checks'),
        args.IsSpecified('iap'),
        args.IsSpecified('port_name'),
        args.IsSpecified('protocol'),
        args.IsSpecified('security_policy'),
        args.IsSpecified('edge_security_policy'),
        args.IsSpecified('session_affinity'),
        args.IsSpecified('timeout'),
        args.IsSpecified('connection_drain_on_failover'),
        args.IsSpecified('drop_traffic_if_unhealthy'),
        args.IsSpecified('failover_ratio'),
        args.IsSpecified('enable_logging'),
        args.IsSpecified('logging_sample_rate'),
        args.IsSpecified('logging_optional'),
        args.IsSpecified('logging_optional_fields'),
        args.IsSpecified('health_checks'),
        args.IsSpecified('https_health_checks'),
        args.IsSpecified('no_health_checks'),
        args.IsSpecified('subsetting_policy'),
        args.IsSpecified('subsetting_subset_size')
        if self._support_subsetting_subset_size
        else False,
        args.IsSpecified('request_coalescing'),
        args.IsSpecified('cache_mode'),
        args.IsSpecified('client_ttl'),
        args.IsSpecified('no_client_ttl'),
        args.IsSpecified('default_ttl'),
        args.IsSpecified('no_default_ttl'),
        args.IsSpecified('max_ttl'),
        args.IsSpecified('no_max_ttl'),
        args.IsSpecified('negative_caching'),
        args.IsSpecified('negative_caching_policy'),
        args.IsSpecified('no_negative_caching_policies'),
        args.IsSpecified('custom_response_header'),
        args.IsSpecified('no_custom_response_headers'),
        args.IsSpecified('serve_while_stale'),
        args.IsSpecified('no_serve_while_stale'),
        args.IsSpecified('bypass_cache_on_request_headers'),
        args.IsSpecified('no_bypass_cache_on_request_headers'),
        args.IsSpecified('connection_persistence_on_unhealthy_backends'),
        args.IsSpecified('tracking_mode'),
        args.IsSpecified('idle_timeout_sec'),
        args.IsSpecified('enable_strong_affinity'),
        args.IsSpecified('compression_mode'),
        args.IsSpecified('service_lb_policy'),
        args.IsSpecified('no_service_lb_policy'),
        args.IsSpecified('service_bindings'),
        args.IsSpecified('no_service_bindings'),
        args.IsSpecified('locality_lb_policy'),
        args.IsSpecified('no_locality_lb_policy'),
        args.IsSpecified('ip_address_selection_policy'),
        args.IsSpecified('external_managed_migration_state'),
        args.IsSpecified('external_managed_migration_testing_percentage'),
        args.IsSpecified('clear_external_managed_migration_state'),
        args.IsSpecified('load_balancing_scheme'),
        args.IsSpecified('tls_settings'),
        args.IsSpecified('no_tls_settings'),
        args.IsSpecified('custom_metrics'),
        args.IsSpecified('custom_metrics_file'),
        args.IsSpecified('clear_custom_metrics'),
        args.IsSpecified('ip_port_dynamic_forwarding')
        if self._support_ip_port_dynamic_forwarding
        else False,
        args.IsSpecified('zonal_affinity_spillover')
        if self._support_zonal_affinity
        else False,
        args.IsSpecified('zonal_affinity_spillover_ratio')
        if self._support_zonal_affinity
        else False,
        args.IsSpecified('allow_multinetwork')
        if self._support_allow_multinetwork
        else False,
    ]):
      raise compute_exceptions.UpdatePropertyError(
          'At least one property must be modified.')

  def GetSetRequest(self, client, backend_service_ref, replacement):
    """Returns a backend service patch request."""

    if (
        backend_service_ref.Collection() == 'compute.backendServices'
        and replacement.failoverPolicy
        ):
      raise exceptions.InvalidArgumentException(
          '--global',
          'failover policy parameters are only for regional passthrough '
          'Network Load Balancers.')

    if backend_service_ref.Collection() == 'compute.regionBackendServices':
      return (
          client.apitools_client.regionBackendServices,
          'Patch',
          client.messages.ComputeRegionBackendServicesPatchRequest(
              project=backend_service_ref.project,
              region=backend_service_ref.region,
              backendService=backend_service_ref.Name(),
              backendServiceResource=replacement),
      )

    return (
        client.apitools_client.backendServices,
        'Patch',
        client.messages.ComputeBackendServicesPatchRequest(
            project=backend_service_ref.project,
            backendService=backend_service_ref.Name(),
            backendServiceResource=replacement),
    )

  def _GetSetSecurityPolicyRequest(self, client, backend_service_ref,
                                   security_policy_ref):
    backend_service = backend_service_client.BackendService(
        backend_service_ref, compute_client=client)
    return backend_service.MakeSetSecurityPolicyRequestTuple(
        security_policy=security_policy_ref)

  def _GetSetEdgeSecurityPolicyRequest(self, client, backend_service_ref,
                                       security_policy_ref):
    backend_service = backend_service_client.BackendService(
        backend_service_ref, compute_client=client)
    return backend_service.MakeSetEdgeSecurityPolicyRequestTuple(
        security_policy=security_policy_ref)

  def GetGetRequest(self, client, backend_service_ref):
    """Create Backend Services get request."""
    if backend_service_ref.Collection() == 'compute.regionBackendServices':
      return (
          client.apitools_client.regionBackendServices,
          'Get',
          client.messages.ComputeRegionBackendServicesGetRequest(
              project=backend_service_ref.project,
              region=backend_service_ref.region,
              backendService=backend_service_ref.Name()),
      )
    return (
        client.apitools_client.backendServices,
        'Get',
        client.messages.ComputeBackendServicesGetRequest(
            project=backend_service_ref.project,
            backendService=backend_service_ref.Name()),
    )

  def _ApplyIapArgs(self, client, iap_arg, existing, replacement):
    """Applies IAP args."""
    if iap_arg is not None:
      existing_iap = existing.iap
      replacement.iap = backend_services_utils.GetIAP(
          iap_arg, client.messages, existing_iap_settings=existing_iap)
      if replacement.iap.enabled and not (existing_iap and
                                          existing_iap.enabled):
        log.warning(backend_services_utils.IapBestPracticesNotice())
      if (replacement.iap.enabled and replacement.protocol
          is not client.messages.BackendService.ProtocolValueValuesEnum.HTTPS):
        log.warning(backend_services_utils.IapHttpWarning())

  def Run(self, args, holder):
    """Issues requests necessary to update the Backend Services."""
    self.ValidateArgs(args)

    client = holder.client

    backend_service_ref = (
        flags.GLOBAL_REGIONAL_BACKEND_SERVICE_ARG.ResolveAsResource(
            args,
            holder.resources,
            scope_lister=compute_flags.GetDefaultScopeLister(client)))
    get_request = self.GetGetRequest(client, backend_service_ref)

    objects = client.MakeRequests([get_request])

    new_object, cleared_fields = self.Modify(client, holder.resources, args,
                                             objects[0], backend_service_ref)

    # If existing object is equal to the proposed object or if
    # Modify() returns None, then there is no work to be done, so we
    # print the resource and return.
    if objects[0] == new_object:
      # Only skip update if security_policy and edge_security_policy are not
      # set.
      if (getattr(args, 'security_policy', None) is None and
          getattr(args, 'edge_security_policy', None) is None):
        log.status.Print(
            'No change requested; skipping update for [{0}].'.format(
                objects[0].name))
        return objects
      backend_service_result = []
    else:
      backend_service_request = self.GetSetRequest(client, backend_service_ref,
                                                   new_object)
      # Cleared list fields need to be explicitly identified for Patch API.
      with client.apitools_client.IncludeFields(cleared_fields):
        backend_service_result = client.MakeRequests([backend_service_request])

    # Empty string is a valid value.
    if getattr(args, 'security_policy', None) is not None:
      if getattr(args, 'security_policy', None):
        security_policy_ref = self.SECURITY_POLICY_ARG.ResolveAsResource(
            args, holder.resources).SelfLink()
      # If security policy is an empty string we should clear the current policy
      else:
        security_policy_ref = None
      security_policy_request = self._GetSetSecurityPolicyRequest(
          client, backend_service_ref, security_policy_ref)
      security_policy_result = client.MakeRequests([security_policy_request])
    else:
      security_policy_result = []

    # Empty string is a valid value.
    if getattr(args, 'edge_security_policy', None) is not None:
      if getattr(args, 'edge_security_policy', None):
        security_policy_ref = self.EDGE_SECURITY_POLICY_ARG.ResolveAsResource(
            args, holder.resources).SelfLink()
      # If security policy is an empty string we should clear the current policy
      else:
        security_policy_ref = None
      edge_security_policy_request = self._GetSetEdgeSecurityPolicyRequest(
          client, backend_service_ref, security_policy_ref)
      edge_security_policy_result = client.MakeRequests(
          [edge_security_policy_request])
    else:
      edge_security_policy_result = []

    return (backend_service_result + security_policy_result +
            edge_security_policy_result)


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class UpdateGA(base.UpdateCommand):
  """Update a backend service.

  *{command}* is used to update backend services.
  """

  _support_subsetting_subset_size = False
  _support_ip_port_dynamic_forwarding = False
  _support_zonal_affinity = False
  _support_allow_multinetwork = False

  @classmethod
  def Args(cls, parser):
    UpdateHelper.Args(
        parser,
        support_subsetting_subset_size=cls._support_subsetting_subset_size,
        support_ip_port_dynamic_forwarding=cls._support_ip_port_dynamic_forwarding,
        support_zonal_affinity=cls._support_zonal_affinity,
        support_allow_multinetwork=cls._support_allow_multinetwork,
    )

  def Run(self, args):
    """Issues requests necessary to update the Backend Services."""
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    return UpdateHelper(
        self._support_subsetting_subset_size,
        support_ip_port_dynamic_forwarding=self._support_ip_port_dynamic_forwarding,
        support_zonal_affinity=self._support_zonal_affinity,
        support_allow_multinetwork=self._support_allow_multinetwork,
        release_track=self.ReleaseTrack(),
    ).Run(args, holder)


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(UpdateGA):
  """Update a backend service.

  *{command}* is used to update backend services.
  """

  _support_subsetting_subset_size = True
  _support_ip_port_dynamic_forwarding = True
  _support_zonal_affinity = True
  _support_allow_multinetwork = False


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(UpdateBeta):
  """Update a backend service.

  *{command}* is used to update backend services.
  """

  _support_subsetting_subset_size = True
  _support_ip_port_dynamic_forwarding = True
  _support_zonal_affinity = True
  _support_allow_multinetwork = True
