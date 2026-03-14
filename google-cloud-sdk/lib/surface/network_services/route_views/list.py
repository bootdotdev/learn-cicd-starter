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
"""List all route views for Meshes or Gateways."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_services import flags
from googlecloudsdk.command_lib.network_services import util


@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA
)
@base.DefaultUniverseOnly
class List(base.ListCommand):
  r"""Route View for a Mesh or Gateway.

  List all Route Views for a Mesh or Gateway

  ## EXAMPLES

  List Route Views for a mesh.

    $ {command} --mesh projects/-/locations/-/meshes/mesh1
    $ {command} --project $PROJECT --location $LOCATION --mesh
    projects/-/locations/-/meshes/mesh1
  List Route Views for a gateway.

    $ {command} --gateway projects/-/locations/-/gateways/gateway1
    $ {command} --project $PROJECT --location $LOCATION --gateway
    projects/-/locations/-/gateways/gateway1
  """

  @staticmethod
  def Args(parser):
    """Set args for route-views list."""
    flags.AddFilteredListFlags(parser)
    flags.AddGatewayAndMeshFlags(parser)

    parser.display_info.AddFormat("""
     table(
        name:label=NAME
      )""")

  def Run(self, args):
    # is there a way to do this automatically?
    name = ""
    if args.IsSpecified("mesh"):
      mesh = args.CONCEPTS.mesh.Parse()
      name = mesh.RelativeName()
    elif args.IsSpecified("gateway"):
      gateway = args.CONCEPTS.gateway.Parse()
      name = gateway.RelativeName()

    return util.ListRouteViews(
        self.ReleaseTrack(), name, args.page_size, args.limit
    )
