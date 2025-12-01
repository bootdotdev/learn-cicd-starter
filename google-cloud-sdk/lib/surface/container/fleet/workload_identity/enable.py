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
"""The command to enable Workload Identity Feature."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from googlecloudsdk.calliope import base


from googlecloudsdk.command_lib.container.fleet.features import base as feature_base


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Enable(feature_base.EnableCommand):
  """Enable Workload Identity Feature.

  Enable the Workload Identity Feature in a fleet.

  ## Examples

  To enable Workload Identity Feature, run:

    $ {command}
  """
  feature_name = 'workloadidentity'
  feature_display_name = 'Workload Identity'

  def Run(self, args):
    # Create an empty feature spec, but explicitly define an empty
    # workloadidentity object. The server will validate this field is not-empty
    # in order to ensure API visiblity labels are enforced when enabling the
    # feature.
    f = self.messages.Feature(
        spec=self.messages.CommonFeatureSpec(
            workloadidentity=self.messages.WorkloadIdentityFeatureSpec()
        )
    )
    return self.Enable(f)
