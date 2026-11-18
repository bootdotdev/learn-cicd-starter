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
"""Command to create Fleet Package."""

from googlecloudsdk.api_lib.container.fleet.packages import fleet_packages as apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet.packages import flags
from googlecloudsdk.command_lib.container.fleet.packages import utils
from googlecloudsdk.command_lib.export import util as export_util
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.core.console import console_io

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To update Fleet Package `cert-manager-app`, run:

          $ {command} cert-manager-app --source=my_source.yaml
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  """Update Package Rollouts Fleet Package."""

  detailed_help = _DETAILED_HELP
  _api_version = 'v1'

  @staticmethod
  def Args(parser):
    flags.AddSourceFlag(parser)
    concept_parsers.ConceptParser.ForResource(
        'fleet_package',
        flags.GetFleetPackageResourceSpec(),
        'The Fleet Package to create.',
        required=True,
        prefixes=False,
    ).AddToParser(parser)

  def Run(self, args):
    """Run the update command."""
    client = apis.FleetPackagesClient(self._api_version)
    data = console_io.ReadFromFileOrStdin(
        utils.ExpandPathForUser(args.source), binary=False
    )
    fleet_package = export_util.Import(
        message_type=client.messages.FleetPackage,
        stream=data,
    )

    possible_attributes = [
        'resourceBundleSelector',
        'target',
        'variantSelector',
        'rolloutStrategy',
        'deletionPropagationPolicy',
        'state',
    ]
    update_mask_attrs = []
    for attr in possible_attributes:
      attr_value = getattr(fleet_package, attr, None)
      if attr_value is not None:
        update_mask_attrs.append(attr)
    update_mask = ','.join(update_mask_attrs)

    fully_qualified_name = f'projects/{flags.GetProject(args)}/locations/{flags.GetLocation(args)}/fleetPackages/{args.fleet_package}'
    fleet_package = utils.UpsertFleetPackageName(
        fleet_package, fully_qualified_name
    )
    fleet_package = utils.FixFleetPackagePathForCloudBuild(fleet_package)

    return client.Update(
        fleet_package=fleet_package,
        name=fully_qualified_name,
        update_mask=update_mask,
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(Update):
  """Update Package Rollouts Fleet Package."""

  _api_version = 'v1beta'


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(Update):
  """Update Package Rollouts Fleet Package."""

  _api_version = 'v1alpha'
