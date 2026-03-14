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
"""Command group for IAM Workforce Pools Providers SCIM Tenants."""

from googlecloudsdk.calliope import base
# NOTE: No longer need hook-specific imports unless other hooks are added later


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class ScimTenants(base.Group):
  """Manage IAM workforce identity pool provider SCIM tenants.

  Commands for creating, describing, listing, updating, and deleting
  SCIM tenants associated with IAM workforce identity pool providers. SCIM
  tenants enable automated user and group provisioning.
  """
