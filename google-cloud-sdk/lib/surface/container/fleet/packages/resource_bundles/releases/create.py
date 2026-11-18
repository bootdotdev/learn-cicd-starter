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
"""Command to create Release."""

from googlecloudsdk.api_lib.container.fleet.packages import releases as apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet.packages import flags
from googlecloudsdk.command_lib.container.fleet.packages import utils

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To create Release `v1.0.0` for Resource Bundle `my-bundle` in `us-central1`, run:

          $ {command} --version=v1.0.0 --resource-bundle=my-bundle --source=manifest.yaml

        To create a Release with multiple variants in one directory, run:

          $ {command} --version=v1.0.0 --resource-bundle=my-bundle --source=/manifests/ --variants-pattern=manifest-*.yaml

        To create a Release with multiple variants across multiple directories, ex:

          $ {command} --version=v1.0.0 --resource-bundle=my-bundle --source=/manifests/ --variants-pattern=dir-*/
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Create(base.CreateCommand):
  """Create Package Rollouts Release."""

  detailed_help = _DETAILED_HELP
  _api_version = 'v1'

  @staticmethod
  def Args(parser):
    flags.AddResourceBundleFlag(parser)
    flags.AddLocationFlag(parser)
    parser.add_argument(
        '--version', required=True, help='Version of the Release to create.'
    )
    flags.AddLifecycleFlag(parser)
    flags.AddVariantsPatternFlag(parser)
    parser.add_argument(
        '--source',
        required=True,
        help="""Source file or directory to create the Release from.
          e.g. ``--source=manifest.yaml'', ``--source=/manifests-dir/''
          Can optionally be paired with the ``--variants-pattern'' arg to create
          multiple variants of a Release.""",
    )
    flags.AddSkipCreatingVariantResourcesFlag(parser)

  def Run(self, args):
    """Run the create command."""
    client = apis.ReleasesClient(self._api_version)
    utils.ValidateSource(args.source)
    glob_pattern = utils.GlobPatternFromSourceAndVariantsPattern(
        args.source, args.variants_pattern
    )
    variants = utils.VariantsFromGlobPattern(glob_pattern)

    return client.Create(
        resource_bundle=args.resource_bundle,
        version=args.version,
        project=flags.GetProject(args),
        location=flags.GetLocation(args),
        lifecycle=args.lifecycle,
        variants=variants,
        skip_creating_variant_resources=args.skip_creating_variant_resources,
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateBeta(Create):
  """Create Package Rollouts Release."""

  _api_version = 'v1beta'


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateAlpha(Create):
  """Create Package Rollouts Release."""

  _api_version = 'v1alpha'
