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
"""Command to update Release."""

from googlecloudsdk.api_lib.container.fleet.packages import releases as apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet.packages import flags

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To update Release `v1.0.0` for Resource Bundle `my-bundle` in `us-central1`, run:

          $ {command} --version=v1.0.0 --resource-bundle=my-bundle --lifecycle=PUBLISHED
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  """Update Package Rollouts Release."""

  detailed_help = _DETAILED_HELP
  _api_version = 'v1'

  @staticmethod
  def Args(parser):
    flags.AddReleaseFlag(parser)
    flags.AddLocationFlag(parser)
    flags.AddResourceBundleFlag(parser)
    flags.AddLifecycleFlag(parser)

  def Run(self, args):
    """Run the update command."""
    client = apis.ReleasesClient(self._api_version)
    update_mask_attrs = []

    if args.lifecycle:
      update_mask_attrs.append('lifecycle')
    update_mask = ','.join(update_mask_attrs)

    return client.Update(
        release=args.release,
        project=flags.GetProject(args),
        location=flags.GetLocation(args),
        resource_bundle=args.resource_bundle,
        lifecycle=args.lifecycle,
        update_mask=update_mask,
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(Update):
  """Update Package Rollouts Release."""

  _api_version = 'v1beta'


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(Update):
  """Update Package Rollouts Release."""

  _api_version = 'v1alpha'
