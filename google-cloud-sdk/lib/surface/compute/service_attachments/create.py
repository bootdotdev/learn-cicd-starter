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
"""Command for creating service attachments."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.forwarding_rules import flags as forwarding_rule_flags
from googlecloudsdk.command_lib.compute.networks.subnets import flags as subnetwork_flags
from googlecloudsdk.command_lib.compute.service_attachments import flags
from googlecloudsdk.command_lib.compute.service_attachments import service_attachments_utils


def _DetailedHelp():
  return {
      'brief':
          'Create a Google Compute Engine service attachment.',
      'DESCRIPTION':
          """\
      *{command}* is used to create service attachments. A service producer
      creates service attachments to make a service available to consumers.
      Service consumers use Private Service Connect endpoints to privately
      forward traffic to the service attachment.
      """,
      'EXAMPLES':
          """\
      If there is an already-created internal load balancer (ILB) with the name
      MY_ILB in region us-central1 and there is an already-created Private
      Service Connect subnets MY_SUBNET1 and MY_SUBNET2, create a service
      attachment pointing to the ILB by running:

        $ {command} SERVICE_ATTACHMENT_NAME --region=us-central1 --producer-forwarding-rule=MY_ILB --connection-preference=ACCEPT_AUTOMATIC --nat-subnets=MY_SUBNET1,MY_SUBNET2

      To create a service attachment with a textual description, run:

        $ {command} SERVICE_ATTACHMENT_NAME --region=us-central1 --producer-forwarding-rule=MY_ILB --connection-preference=ACCEPT_AUTOMATIC --nat-subnets=MY_SUBNET1,MY_SUBNET2 --description='default service attachment'

      """,
  }


class CreateHelper(object):
  """Helper class to create a service attachment."""

  SERVICE_ATTACHMENT_ARG = None
  PRODUCER_FORWARDING_RULE_ARG = None
  NAT_SUBNETWORK_ARG = None

  def __init__(self, holder):
    self._holder = holder

  @classmethod
  def Args(cls, parser):
    """Create a Google Compute Engine service attachment.

    Args:
      parser: the parser that parses the input from the user.
    """
    cls.SERVICE_ATTACHMENT_ARG = flags.ServiceAttachmentArgument()
    cls.SERVICE_ATTACHMENT_ARG.AddArgument(parser, operation_type='create')
    cls.PRODUCER_FORWARDING_RULE_ARG = (
        forwarding_rule_flags.ForwardingRuleArgumentForServiceAttachment()
    )
    cls.NAT_SUBNETWORK_ARG = (
        subnetwork_flags.SubnetworkArgumentForServiceAttachment()
    )
    cls.NAT_SUBNETWORK_ARG.AddArgument(parser)

    parser.display_info.AddFormat(flags.DEFAULT_LIST_FORMAT)
    parser.display_info.AddCacheUpdater(flags.ServiceAttachmentsCompleter)

    flags.AddDescription(parser)
    flags.AddTargetServiceAndProducerForwardingRuleArgs(parser)
    flags.AddConnectionPreference(parser, is_update=False)
    flags.AddEnableProxyProtocolForCreate(parser)
    flags.AddReconcileConnectionsForCreate(parser)
    flags.AddConsumerRejectList(parser)
    flags.AddConsumerAcceptListOld(parser)
    flags.AddDomainNames(parser)
    flags.AddPropagatedConnectionLimit(parser)

  def Run(self, args):
    """Issue a service attachment INSERT request."""
    client = self._holder.client
    service_attachment_ref = self.SERVICE_ATTACHMENT_ARG.ResolveAsResource(
        args,
        self._holder.resources,
        default_scope=compute_scope.ScopeEnum.REGION,
    )
    producer_forwarding_rule_ref = (
        self.PRODUCER_FORWARDING_RULE_ARG.ResolveAsResource(
            args,
            self._holder.resources,
            default_scope=compute_scope.ScopeEnum.REGION,
        )
    )
    if target_service_args := args.target_service:
      target_service = target_service_args
      producer_forwarding_rule = None
    elif producer_forwarding_rule_ref:
      producer_forwarding_rule = producer_forwarding_rule_ref.SelfLink()
      target_service = producer_forwarding_rule_ref.SelfLink()
    nat_subnetwork_refs = self.NAT_SUBNETWORK_ARG.ResolveAsResource(
        args,
        self._holder.resources,
        default_scope=compute_scope.ScopeEnum.REGION,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
    )
    nat_subnetworks = [
        nat_subnetwork_ref.SelfLink()
        for nat_subnetwork_ref in nat_subnetwork_refs
    ]
    connection_preference = service_attachments_utils.GetConnectionPreference(
        args, client.messages)
    enable_proxy_protocol = args.enable_proxy_protocol

    service_attachment = client.messages.ServiceAttachment(
        description=args.description,
        name=service_attachment_ref.Name(),
        natSubnets=nat_subnetworks,
        connectionPreference=connection_preference,
        enableProxyProtocol=enable_proxy_protocol,
        producerForwardingRule=producer_forwarding_rule,
        targetService=target_service,
    )

    if args.IsSpecified('consumer_reject_list'):
      service_attachment.consumerRejectLists = args.consumer_reject_list
    if args.IsSpecified('consumer_accept_list'):
      accept_list = service_attachments_utils.GetConsumerAcceptList(
          args, client.messages)
      service_attachment.consumerAcceptLists = accept_list
    if args.IsSpecified('domain_names'):
      service_attachment.domainNames = args.domain_names
    if args.IsSpecified('reconcile_connections'):
      service_attachment.reconcileConnections = args.reconcile_connections
    if args.IsSpecified('propagated_connection_limit'):
      service_attachment.propagatedConnectionLimit = (
          args.propagated_connection_limit
      )

    request = client.messages.ComputeServiceAttachmentsInsertRequest(
        project=service_attachment_ref.project,
        region=service_attachment_ref.region,
        serviceAttachment=service_attachment)
    collection = client.apitools_client.serviceAttachments
    return client.MakeRequests([(collection, 'Insert', request)])


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.GA,
)
class Create(base.CreateCommand):
  """Create a Google Compute Engine service attachment."""

  detailed_help = _DetailedHelp()

  @classmethod
  def Args(cls, parser):
    CreateHelper.Args(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    return CreateHelper(holder).Run(args)


@base.ReleaseTracks(
    base.ReleaseTrack.BETA,
)
class CreateBeta(Create):
  """Create a Google Compute Engine service attachment."""

  detailed_help = _DetailedHelp()


@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA,
)
class CreateAlpha(Create):
  """Create a Google Compute Engine service attachment."""

  detailed_help = _DetailedHelp()
