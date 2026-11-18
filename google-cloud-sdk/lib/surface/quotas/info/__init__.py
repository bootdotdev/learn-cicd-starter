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
"""The command group for Cloud Quotas Quota Info."""

from googlecloudsdk.calliope import base


# We could have multiple tracks here, e.g.
#   @base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.ALPHA)
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class QuotaInfoAlpha(base.Group):
  """Manage Cloud Quotas QuotaInfo.

  QuotaInfo is a read-only resource that provides metadata and quota value
  information about a particular quota for a given project, folder or
  organization. The QuotaInfo resource contains:

  * Metadata such as name and dimension.
  * Quota values for different quota dimensions.

  Cloud Quotas obtains information from the quotas defined by Google Cloud
  services and any fulfilled quota adjustments that you initiate.

  Note: Because QuotaInfo is constructed by incorporating information from
  different sources, a default quota configuration exists even if you have not
  created a QuotaPreference resource. Until you express a preferred state
  through quotaPreference.create or quotaPreference.update, QuotaInfo relies on
  the default quota information available to determine what quota value to
  enforce.
  """


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.UniverseCompatible
class QuotaInfoBeta(base.Group):
  """Manage Cloud Quotas QuotaInfo.

  QuotaInfo is a read-only resource that provides metadata and quota value
  information about a particular quota for a given project, folder or
  organization. The QuotaInfo resource contains:

  * Metadata such as name and dimension.
  * Quota values for different quota dimensions.

  Cloud Quotas obtains information from the quotas defined by Google Cloud
  services and any fulfilled quota adjustments that you initiate.

  Note: Because QuotaInfo is constructed by incorporating information from
  different sources, a default quota configuration exists even if you have not
  created a QuotaPreference resource. Until you express a preferred state
  through quotaPreference.create or quotaPreference.update, QuotaInfo relies on
  the default quota information available to determine what quota value to
  enforce.
  """
