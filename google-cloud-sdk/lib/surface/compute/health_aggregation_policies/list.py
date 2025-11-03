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
"""Command for listing health aggregation policies."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import lister
from googlecloudsdk.calliope import base


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class List(base.ListCommand):
  """List health aggregation policies."""

  messages = None

  @staticmethod
  def Args(parser):
    lister.AddRegionsArg(parser)
    parser.display_info.AddFormat("""
                                  table(
                                      name:label=NAME,
                                      region.basename():label=REGION,
                                      healthyPercentThreshold:label=HEALTHY_PERCENT_THRESHOLD,
                                      minHealthyThreshold:label=MIN_HEALTHY_THRESHOLD,
                                      policyType:label=POLICY_TYPE
                                  )
                                  """)

  def Collection(self):
    """Override the default collection from the base class."""
    return None

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    self.messages = client.messages

    request_data = lister.ParseMultiScopeFlags(args, holder.resources)

    list_implementation = lister.MultiScopeLister(
        client,
        regional_service=client.apitools_client.regionHealthAggregationPolicies,
        aggregation_service=client.apitools_client.regionHealthAggregationPolicies,
    )

    return lister.Invoke(request_data, list_implementation)

  @property
  def service(self):
    return self.compute.regionHealthAggregationPolicies

  @property
  def resource_type(self):
    return 'regionHealthAggregationPolicies'

  @property
  def regional_service(self):
    """The service used to list regional resources."""
    return self.compute.regionHealthAggregationPolicies

  @property
  def aggregation_service(self):
    """The service used to get aggregated list of resources."""
    return self.compute.regionHealthAggregationPolicies
