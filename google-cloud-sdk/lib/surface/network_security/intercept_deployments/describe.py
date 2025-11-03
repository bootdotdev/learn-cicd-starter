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
"""Describe deployment command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_security.intercept_deployments import api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security.intercept import deployment_flags

DETAILED_HELP = {
    'DESCRIPTION': """
          Describe an intercept deployment.

          For more examples, refer to the EXAMPLES section below.

        """,
    'EXAMPLES': """
            To get a description of an intercept deployment called `my-deployment` in
            zone `us-central1-a`, run:

            $ {command} my-deployment --location=us-central1-a --project=my-project

            OR

            $ {command} projects/my-project/locations/us-central1-a/interceptDeployments/my-deployment
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Describe(base.DescribeCommand):
  """Describe an Intercept Deployment."""

  @classmethod
  def Args(cls, parser):
    deployment_flags.AddDeploymentResource(cls.ReleaseTrack(), parser)

  def Run(self, args):
    client = api.Client(self.ReleaseTrack())

    deployment = args.CONCEPTS.intercept_deployment.Parse()

    return client.DescribeDeployment(name=deployment.RelativeName())


Describe.detailed_help = DETAILED_HELP
