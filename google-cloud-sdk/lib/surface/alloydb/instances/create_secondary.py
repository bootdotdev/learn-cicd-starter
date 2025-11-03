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
"""Creates a new AlloyDB secondary instance."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.alloydb import api_util
from googlecloudsdk.api_lib.alloydb import instance_operations
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.alloydb import flags
from googlecloudsdk.command_lib.alloydb import instance_helper
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources


# TODO(b/312466999): Change @base.DefaultUniverseOnly to
# @base.UniverseCompatible once b/312466999 is fixed.
# See go/gcloud-cli-running-tpc-tests.
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class CreateSecondary(base.CreateCommand):
  """Creates a new AlloyDB SECONDARY instance within a given cluster."""

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
        To create a new secondary instance, run:

          $ {command} my-instance --cluster=my-cluster --region=us-central1
        """,
  }

  @staticmethod
  def Args(parser):
    """Specifies additional command flags.

    Args:
      parser: argparse.Parser: Parser object for command line inputs
    """
    base.ASYNC_FLAG.AddToParser(parser)
    flags.AddCluster(parser, False)
    flags.AddAvailabilityType(parser)
    flags.AddInstance(parser)
    flags.AddRegion(parser)
    flags.AddDatabaseFlags(parser)
    flags.AddSSLMode(parser, default_from_primary=True)
    flags.AddRequireConnectors(parser)
    flags.AddAssignInboundPublicIp(parser)
    flags.AddAuthorizedExternalNetworks(parser)
    flags.AddOutboundPublicIp(parser, show_negated_in_help=True)
    flags.AddAllowedPSCProjects(parser)
    flags.AddPSCNetworkAttachmentUri(parser)
    flags.AddPSCAutoConnections(parser)
    flags.AddAllocatedIPRangeOverride(parser)

    # Connection pooling flags.
    flags.AddEnableConnectionPooling(parser)
    flags.AddConnectionPoolingPoolMode(parser)
    flags.AddConnectionPoolingMinPoolSize(parser)
    flags.AddConnectionPoolingMaxPoolSize(parser)
    flags.AddConnectionPoolingMaxClientConnections(parser)
    flags.AddConnectionPoolingServerIdleTimeout(parser)
    flags.AddConnectionPoolingQueryWaitTimeout(parser)
    flags.AddConnectionPoolingStatsUsers(parser)
    flags.AddConnectionPoolingIgnoreStartupParameters(parser)
    flags.AddConnectionPoolingServerLifetime(parser)
    flags.AddConnectionPoolingClientConnectionIdleTimeout(parser)
    flags.AddConnectionPoolingMaxPreparedStatements(parser)

  def ConstructSecondaryCreateRequestFromArgs(
      self, client, alloydb_messages, cluster_ref, args
  ):
    return instance_helper.ConstructSecondaryCreateRequestFromArgsGA(
        client, alloydb_messages, cluster_ref, args
    )

  def Run(self, args):
    """Constructs and sends request.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      ProcessHttpResponse of the request made.
    """
    client = api_util.AlloyDBClient(self.ReleaseTrack())
    alloydb_client = client.alloydb_client
    alloydb_messages = client.alloydb_messages
    cluster_ref = client.resource_parser.Create(
        'alloydb.projects.locations.clusters',
        projectsId=properties.VALUES.core.project.GetOrFail,
        locationsId=args.region,
        clustersId=args.cluster,
    )
    req = self.ConstructSecondaryCreateRequestFromArgs(
        client, alloydb_messages, cluster_ref, args
    )

    op = alloydb_client.projects_locations_clusters_instances.Createsecondary(
        req
    )
    op_ref = resources.REGISTRY.ParseRelativeName(
        op.name, collection='alloydb.projects.locations.operations'
    )
    log.status.Print('Operation ID: {}'.format(op_ref.Name()))
    if not args.async_:
      instance_operations.Await(
          op_ref, 'Creating secondary instance', self.ReleaseTrack()
      )
    return op


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateSecondaryBeta(CreateSecondary):
  """Creates a new AlloyDB SECONDARY instance within a given cluster."""

  @classmethod
  def Args(cls, parser):
    super(CreateSecondaryBeta, CreateSecondaryBeta).Args(parser)

  def ConstructSecondaryCreateRequestFromArgs(
      self, client, alloydb_messages, cluster_ref, args
  ):
    return instance_helper.ConstructSecondaryCreateRequestFromArgsBeta(
        client, alloydb_messages, cluster_ref, args
    )


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateSecondaryAlpha(CreateSecondaryBeta):
  """Creates a new AlloyDB SECONDARY instance within a given cluster."""

  @classmethod
  def Args(cls, parser):
    super(CreateSecondaryAlpha, CreateSecondaryAlpha).Args(parser)

  def ConstructSecondaryCreateRequestFromArgs(
      self, client, alloydb_messages, cluster_ref, args
  ):
    return instance_helper.ConstructSecondaryCreateRequestFromArgsAlpha(
        client, alloydb_messages, cluster_ref, args
    )
