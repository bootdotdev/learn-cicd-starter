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
from surface.run.services import update


@base.ReleaseTracks(base.ReleaseTrack.GA)
class MultiRegionUpdate(update.Update):
  """Update environment variables, add/remove regions, and other configuration settings in Multi-Region Services."""

  @classmethod
  def Args(cls, parser):
    update.Update.Args(parser)
    flags.AddAddRegionsArg(parser)
    flags.AddRemoveRegionsArg(parser)

  def _ConnectionContext(self, args):
    return connection_context.GetConnectionContext(
        args,
        flags.Product.RUN,
        self.ReleaseTrack(),
        is_multiregion=True,
    )

  def _GetBaseChanges(self, args, existing_service=None):
    changes = (
        flags.GetServiceConfigurationChanges(args, base.ReleaseTrack) or []
    )
    if flags.FlagIsExplicitlySet(
        args, 'add_regions'
    ) or flags.FlagIsExplicitlySet(args, 'remove_regions'):
      changes.append(
          config_changes.RegionsChangeAnnotationChange(
              to_add=args.add_regions,
              to_remove=args.remove_regions,
          )
      )
      super()._AssertChanges(
          changes,
          super().input_flags + ', `--add-regions`, `remove-regions`',
          ignore_empty=False,
      )
    ch2 = super()._GetBaseChanges(args, existing_service, ignore_empty=True)
    return ch2 + changes

  def _GetMultiRegionRegions(self, changes, service):
    if not service:
      return None
    modified = config_changes.WithChanges(service, changes)
    annotation = (
        modified.annotations.get(k8s_object.MULTI_REGION_REGIONS_ANNOTATION)
        or None
    )
    return annotation.split(',') if annotation else None

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
          ' --add-regions or --remove-regions instead.',
      )
    return super().Run(args)


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class MultiRegionBetaUpdate(MultiRegionUpdate):
  """Update environment variables, add/remove regions, and other configuration settings in Multi-Region Services."""

  @classmethod
  def Args(cls, parser):
    update.BetaUpdate.Args(parser)
    flags.AddAddRegionsArg(parser)
    flags.AddRemoveRegionsArg(parser)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class MultiRegionAlphaUpdate(MultiRegionBetaUpdate):
  """Update environment variables, add/remove regions, and other configuration settings in Multi-Region Services."""

  @classmethod
  def Args(cls, parser):
    update.AlphaUpdate.Args(parser)
    flags.AddAddRegionsArg(parser)
    flags.AddRemoveRegionsArg(parser)
