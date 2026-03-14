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
"""Command for updating multi-region Services."""

from googlecloudsdk.api_lib.run import k8s_object
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exceptions
from googlecloudsdk.command_lib.run import config_changes
from googlecloudsdk.command_lib.run import connection_context
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import platforms
from googlecloudsdk.command_lib.run import pretty_print
from surface.run.services import replace


@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class MultiRegionReplace(replace.Replace):
  """Create or Update multi-region service from YAML."""

  @classmethod
  def Args(cls, parser):
    replace.Replace.Args(parser)
    flags.AddRegionsArg(parser)
    flags.AddAddRegionsArg(parser)
    flags.AddRemoveRegionsArg(parser)

  def _GetMultiRegionSettings(self, args):
    added_or_removed = flags.FlagIsExplicitlySet(
        args, 'add_regions'
    ) or flags.FlagIsExplicitlySet(args, 'remove_regions')
    all_regions = flags.FlagIsExplicitlySet(args, 'regions')
    if added_or_removed and all_regions:
      raise c_exceptions.InvalidArgumentException(
          parameter_name='--regions',
          message=(
              'Cannot specify --add-regions or --remove-regions with --regions'
          ),
      )
    return all_regions, added_or_removed

  def _GetBaseChanges(self, new_service, args):
    if not new_service:
      return None
    all_regions, added_or_removed = self._GetMultiRegionSettings(args)
    changes = super()._GetBaseChanges(new_service, args)
    if added_or_removed:
      changes.append(
          config_changes.RegionsChangeAnnotationChange(
              to_add=args.add_regions,
              to_remove=args.remove_regions,
          )
      )
    if all_regions:
      changes.append(config_changes.SetRegionsAnnotationChange(args.regions))
    return changes

  def _ConnectionContext(self, args, region_label):
    return connection_context.GetConnectionContext(
        args,
        flags.Product.RUN,
        self.ReleaseTrack(),
        region_label=region_label,
        is_multiregion=True,
    )

  def _GetMultiRegionRegions(self, args, new_service, changes):
    if not new_service:
      return None
    # If the user set --regions, then we just use that. Otherwise, we need to
    # parse the changes to figure out what regions are being added/removed.
    all_regions, added_or_removed = self._GetMultiRegionSettings(args)
    if all_regions:
      return args.regions.split(',')
    if added_or_removed:
      modified = config_changes.WithChanges(new_service, changes)
      annotation = (
          modified.annotations.get(k8s_object.MULTI_REGION_REGIONS_ANNOTATION)
          or None
      )
      return annotation.split(',') if annotation else None
    return None

  def _PrintSuccessMessage(self, service_obj, dry_run, args):
    if args.async_:
      pretty_print.Success(
          'New configuration for [{{bold}}{serv}{{reset}}] is being applied '
          'asynchronously.'.format(serv=service_obj.name)
      )
    elif dry_run:
      pretty_print.Success(
          'New configuration has been validated for Multi-region service '
          '[{{bold}}{serv}{{reset}}].'.format(serv=service_obj.name)
      )
    else:
      pretty_print.Success(
          'New configuration has been applied to Multi-region service '
          '[{{bold}}{serv}{{reset}}].\nRegional URLs:'.format(
              serv=service_obj.name
          )
      )
      for url in service_obj.urls:
        pretty_print.Success('{{bold}}{url}{{reset}}'.format(url=url))

  def Run(self, args):
    if platforms.GetPlatform() != platforms.PLATFORM_MANAGED:
      raise c_exceptions.InvalidArgumentException(
          '--platform',
          'Multi-region Services are only supported on managed platform.',
      )
    if flags.FlagIsExplicitlySet(args, 'region'):
      raise c_exceptions.InvalidArgumentException(
          '--region',
          'Multi-region Services do not support the --region flag. Use'
          ' --regions, --add-regions, or --remove-regions instead.',
      )
    return super().Run(args)
