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
"""Describe the FloorSetting resource."""

from googlecloudsdk.api_lib.model_armor import api as model_armor_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.model_armor import args as model_armor_args


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class DescribeAlpha(base.DescribeCommand):
  """Describe the FloorSetting resource.

  Displays the floor setting resource with the given name.
  """

  @staticmethod
  def Args(parser):
    model_armor_args.AddFullUri(
        parser,
        positional=False,
        help_text='Full uri of the floor setting',
    )

  def Run(self, args):
    api_version = model_armor_api.GetApiFromTrack(self.ReleaseTrack())
    return model_armor_api.FloorSettings(api_version=api_version).Get(
        args.full_uri
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class DescribeBeta(base.DescribeCommand):
  """Describe the FloorSetting resource.

  Displays the floor setting resource with the given name.
  """

  @staticmethod
  def Args(parser):
    model_armor_args.AddFullUri(
        parser,
        positional=False,
        help_text='Full uri of the floor setting',
    )

  def Run(self, args):
    api_version = model_armor_api.GetApiFromTrack(self.ReleaseTrack())
    return model_armor_api.FloorSettings(api_version=api_version).Get(
        args.full_uri
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Describe(base.DescribeCommand):
  """Describe the FloorSetting resource.

  Displays the floor setting resource with the given name.
  """

  @staticmethod
  def Args(parser):
    model_armor_args.AddFullUri(
        parser,
        positional=False,
        help_text='Full uri of the floor setting',
    )

  def Run(self, args):
    api_version = model_armor_api.GetApiFromTrack(self.ReleaseTrack())
    return model_armor_api.FloorSettings(api_version=api_version).Get(
        args.full_uri
    )
