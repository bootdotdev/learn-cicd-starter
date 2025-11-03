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
"""The resource-bundles command group for the Package Rollouts CLI."""

from googlecloudsdk.calliope import base


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class ResourceBundles(base.Group):
  """Commands for managing Package Rollouts Resource Bundles.

  See `gcloud container fleet packages resource-bundles --help` for help.
  """


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class ResourceBundlesBeta(ResourceBundles):
  """Commands for managing Package Rollouts Resource Bundles.

  See `gcloud beta container fleet packages resource-bundles --help` for help.
  """


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ResourceBundlesAlpha(ResourceBundles):
  """Commands for managing Package Rollouts Resource Bundles.

  See `gcloud alpha container fleet packages resource-bundles --help` for help.
  """
