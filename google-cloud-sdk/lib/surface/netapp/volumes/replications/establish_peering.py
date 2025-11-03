# -*- coding: utf-8 -*- #
# Copyright 2024 Google LLC. All Rights Reserved.
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
"""Establish peering for Hybrid replication."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.netapp.volumes.replications import client as replications_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp import flags
from googlecloudsdk.command_lib.netapp.volumes.replications import flags as replications_flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class EstablishPeering(base.Command):
  """Establish peering for Hybrid replication."""

  _RELEASE_TRACK = base.ReleaseTrack.GA

  detailed_help = {
      'DESCRIPTION': """\
          Establish peering for Hybrid replication.
          """,
      'EXAMPLES': """\
          The following command establishes peering for Hybrid replication named NAME using the arguments specified:

              $ {command} NAME --volume=volume1 --peer-cluster-name=peer-cluster-name1 --peer-svm-name=peer-svm-name1 --peer-volume-name=peer-volume-name1 --peer-ip-addresses=1.1.1.1,2.2.2.2
          """,
  }

  @staticmethod
  def Args(parser):
    """Add args for establishing peering for Hybrid replication."""
    concept_parsers.ConceptParser([
        flags.GetReplicationPresentationSpec(
            'The Hybrid replication to establish peering for.'
        )
    ]).AddToParser(parser)
    flags.AddResourcePeerClusterNameArg(parser)
    flags.AddResourcePeerSvmNameArg(parser)
    flags.AddResourcePeerVolumeNameArg(parser)
    flags.AddResourcePeerIpAddressesArg(parser)
    replications_flags.AddReplicationVolumeArg(parser)
    flags.AddResourceAsyncFlag(parser)

  def Run(self, args):
    """Run the establish peering command."""
    replication_ref = args.CONCEPTS.replication.Parse()

    client = replications_client.ReplicationsClient(
        release_track=self._RELEASE_TRACK
    )

    establish_peering_request_config = (
        client.ParseEstablishPeeringRequestConfig(
            args.peer_cluster_name,
            args.peer_svm_name,
            args.peer_volume_name,
            args.peer_ip_addresses,
        )
    )

    replication = client.EstablishPeering(
        replication_ref,
        establish_peering_request_config,
        args.async_,
    )
    return replication


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class EstablishPeeringBeta(EstablishPeering):
  """Establish peering for Hybrid replication."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class EstablishPeeringAlpha(EstablishPeeringBeta):
  """Establish peering for Hybrid replication."""

  _RELEASE_TRACK = base.ReleaseTrack.ALPHA
