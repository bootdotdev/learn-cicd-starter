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
"""List deployments command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_security.mirroring_deployments import api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security import deployment_flags

DETAILED_HELP = {
    'DESCRIPTION': """
          List mirroring deployments.

          For more examples, refer to the EXAMPLES section below.

        """,
    'EXAMPLES': """
            To list mirroring deployments in project `my-project` and zone `us-central1-a`, run:

            $ {command} --project=my-project --location=us-central1-a

            To list mirroring deployments from all zones, run:

            $ {command} --project=my-project --location=-
        """,
}

_FORMAT = """\
table(
    name.scope("mirroringDeployments"):label=ID,
    name.scope("locations").segment(0):label=LOCATION,
    state
)
"""


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
class List(base.ListCommand):
  """List Mirroring Deployments."""

  @classmethod
  def Args(cls, parser):
    parser.display_info.AddFormat(_FORMAT)
    parser.display_info.AddUriFunc(
        deployment_flags.MakeGetUriFunc(cls.ReleaseTrack())
    )
    deployment_flags.AddLocationResourceArg(
        parser, 'Zone of the deployment', '-'
    )

  def Run(self, args):
    client = api.Client(self.ReleaseTrack())

    parent_ref = args.CONCEPTS.location.Parse()

    return client.ListDeployments(parent_ref.RelativeName(),
                                  page_size=args.page_size)


List.detailed_help = DETAILED_HELP
