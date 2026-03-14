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
"""Describe deployment group command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_security.mirroring_deployment_groups import api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security import deployment_group_flags

DETAILED_HELP = {
    'DESCRIPTION': """
          Describe a mirroring deployment group.

          For more examples, refer to the EXAMPLES section below.

        """,
    'EXAMPLES': """
            To get a description of a mirroring deployment group called `my-deployment-group` in
            project ID `my-project`, run:

            $ {command} my-deployment-group --project=my-project --location=global

            OR

            $ {command} projects/my-project/locations/global/mirroringDeploymentGroups/my-deployment-group

        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
class Describe(base.DescribeCommand):
  """Describe a Mirroring Deployment Group."""

  @classmethod
  def Args(cls, parser):
    deployment_group_flags.AddDeploymentGroupResource(
        cls.ReleaseTrack(), parser
    )

  def Run(self, args):
    client = api.Client(self.ReleaseTrack())

    deployment_group = args.CONCEPTS.mirroring_deployment_group.Parse()

    return client.DescribeDeploymentGroup(deployment_group.RelativeName())


Describe.detailed_help = DETAILED_HELP
