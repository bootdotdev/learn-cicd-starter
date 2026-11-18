# -*- coding: utf-8 -*- #
# Copyright 2022 Google LLC. All Rights Reserved.
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
"""The command to describe the status of the Identity Service Feature."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import operator

from googlecloudsdk.api_lib.container.fleet import client
from googlecloudsdk.calliope import base as calliope_base
from googlecloudsdk.command_lib.container.fleet.features import base
from googlecloudsdk.core.util import times


class Describe(base.FeatureCommand, calliope_base.ListCommand):
  """Prints the status of all clusters with Identity Service installed.

  Prints the status of the Identity Service Feature resource in a fleet.

  ## EXAMPLES

  To describe the status of the Identity Service configuration, run:

    $ {command}

  """

  feature_name = 'identityservice'

  @classmethod
  def Args(cls, parser):
    pass

  def Run(self, args):
    feature = self.GetFeature()

    specs = client.HubClient.ToPyDict(feature.membershipSpecs)
    for _, spec in specs.items():
      self.FormatSessionDuration(spec, 'identityservice.identityServiceOptions')
    feature.membershipSpecs = self.hubclient.ToMembershipSpecs(specs)

    states = client.HubClient.ToPyDict(feature.membershipStates)
    for _, state in states.items():
      self.FormatSessionDuration(
          state, 'identityservice.memberConfig.identityServiceOptions'
      )
    feature.membershipStates = self.hubclient.ToProtoMap(
        self.messages.Feature.MembershipStatesValue, states
    )

    default_config = feature.fleetDefaultMemberConfig
    self.FormatSessionDuration(
        default_config, 'identityservice.identityServiceOptions'
    )

    return {'Identity Service Feature': feature}

  def FormatSessionDuration(self, config, path):
    try:
      identity_service_options = operator.attrgetter(path)(config)
      if identity_service_options.sessionDuration is not None:
        session_duration_secs = times.ParseDuration(
            identity_service_options.sessionDuration, default_suffix='s'
        ).total_seconds
        session_duration_mins = int(session_duration_secs/60)
        identity_service_options.sessionDuration = (
            str(session_duration_mins) + ' mins'
        )
    except AttributeError:
      pass
