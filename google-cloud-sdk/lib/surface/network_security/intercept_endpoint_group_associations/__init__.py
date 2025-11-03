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
"""Command sub-group for Intercept Endpoint Group Associations."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base


DETAILED_HELP = {
    'brief': 'Manage Intercept Endpoint Group Association resources.',
    'DESCRIPTION': """
        The gcloud intercept-endpoint-group-associations command group lets you
        associate and deassociate networks to your Intercept Endpoint Group.
        """
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class InterceptEndpointGroupAssociations(base.Group):
  """Manage Intercept Endpoint Group Association resources."""

  category = base.NETWORK_SECURITY_CATEGORY

  detailed_help = DETAILED_HELP
