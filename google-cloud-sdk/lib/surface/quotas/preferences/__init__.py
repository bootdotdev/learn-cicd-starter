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
"""The command group for Cloud Quotas Quota Preference."""

from googlecloudsdk.calliope import base


# We could have multiple tracks here, e.g.
#   @base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.ALPHA)
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class QuotaPreferencesAlpha(base.Group):
  """Manage Cloud Quotas QuotaPreferences.

  A QuotaPreference resource represents your preference for a particular
  dimension combination. Use this resource to make quota increase adjustments to
  quotas in your projects and to make quota decrease adjustments to quotas in
  your projects, folders or organizations. Quota increase adjustments are
  subject to approval and fulfillment. Quota decreases are fulfilled
  immediately. Use the Cloud Quotas console UI or API to set a quota preference.
  """


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.UniverseCompatible
class QuotaPreferencesBeta(base.Group):
  """Manage Cloud Quotas QuotaPreferences.

  A QuotaPreference resource represents your preference for a particular
  dimension combination. Use this resource to make quota increase adjustments to
  quotas in your projects and to make quota decrease adjustments to quotas in
  your projects, folders or organizations. Quota increase adjustments are
  subject to approval and fulfillment. Quota decreases are fulfilled
  immediately. Use the Cloud Quotas console UI or API to set a quota preference.
  """
