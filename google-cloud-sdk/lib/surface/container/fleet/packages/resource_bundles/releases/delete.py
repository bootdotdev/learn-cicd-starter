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
"""Command to delete a Release."""

from googlecloudsdk.api_lib.container.fleet.packages import releases as apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet.packages import flags

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To delete Release `v1.0.0` of `cert-manager` in `us-central1`, run:

          $ {command} v1.0.0 --location=us-central1 --resource-bundle=cert-manager
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Delete(base.DeleteCommand):
  """Delete Package Rollouts Release."""

  detailed_help = _DETAILED_HELP
  _api_version = 'v1'

  @staticmethod
  def Args(parser):
    flags.AddReleaseFlag(parser)
    flags.AddLocationFlag(parser)
    flags.AddResourceBundleFlag(parser)
    flags.AddForceDeleteFlag(parser, 'Release')

  def Run(self, args):
    """Run the delete command."""
    client = apis.ReleasesClient(self._api_version)
    return client.Delete(
        release=args.release,
        project=flags.GetProject(args),
        location=flags.GetLocation(args),
        resource_bundle=args.resource_bundle,
        force=args.force,
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class DeleteBeta(Delete):
  """Delete Package Rollouts Release."""

  _api_version = 'v1beta'


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class DeleteAlpha(Delete):
  """Delete Package Rollouts Release."""

  _api_version = 'v1alpha'
