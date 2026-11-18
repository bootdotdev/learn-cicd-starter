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
"""Establish peering for Cache Volumes."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.netapp.volumes import client as volumes_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp import flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers


@base.Hidden  # TODO(b/423515496): Remove hidden flag once the feature is ready.
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class EstablishPeering(base.Command):
  """Establish peering for Cache Volumes."""

  _RELEASE_TRACK = base.ReleaseTrack.ALPHA

  detailed_help = {
      'DESCRIPTION': """\
          Establish peering for Cache Volumes.
          """,
      'EXAMPLES': """\
          The following command establishes peering for Cache Volume named NAME using the arguments specified:

              $ {command} NAME --location=us-central1 --peer-cluster-name=peer-cluster-name1 --peer-svm-name=peer-svm-name1 --peer-volume-name=peer-volume-name1 --peer-ip-addresses=1.1.1.1,2.2.2.2
          """,
  }

  @staticmethod
  def Args(parser):
    """Add args for establishing peering for Cache Volume."""
    concept_parsers.ConceptParser([
        flags.GetVolumePresentationSpec(
            'The Cache Volume to establish peering for.'
        )
    ]).AddToParser(parser)
    flags.AddResourcePeerClusterNameArg(parser)
    flags.AddResourcePeerSvmNameArg(parser)
    flags.AddResourcePeerVolumeNameArg(parser)
    flags.AddResourcePeerIpAddressesArg(parser)
    flags.AddResourceAsyncFlag(parser)

  def Run(self, args):
    """Run the establish peering command."""
    volume_ref = args.CONCEPTS.volume.Parse()

    client = volumes_client.VolumesClient(
        release_track=self._RELEASE_TRACK
    )

    establish_volume_peering_request_config = (
        client.ParseEstablishVolumePeeringRequestConfig(
            args.peer_cluster_name,
            args.peer_svm_name,
            args.peer_volume_name,
            args.peer_ip_addresses,
        )
    )

    volume = client.EstablishPeering(
        volume_ref,
        establish_volume_peering_request_config,
        args.async_,
    )
    return volume


@base.Hidden  # TODO(b/423515496): Remove hidden flag once the feature is ready.
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class EstablishPeeringBeta(EstablishPeering):
  """Establish peering for Cache Volumes."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA


# @base.Hidden  # TODO(b/423515496): Uncomment this and make EstablishPeering
# point to GA release track for GA launch.
# @base.ReleaseTracks(base.ReleaseTrack.ALPHA)
# class EstablishPeeringAlpha(EstablishPeeringBeta):
#   """Establish peering for Cache Volumes."""

#   _RELEASE_TRACK = base.ReleaseTrack.ALPHA

