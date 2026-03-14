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
class Describe(base.DescribeCommand):
  r"""Route View for a Mesh or Gateway.

  Describe a Route Views for a Mesh or Gateway

  ## EXAMPLES
  Describe a Route Views for a Mesh

    $ {command} --project=$PROJECT_ID --location=$LOCATION --mesh mesh1
    --route-view $ROUTE_VIEW_ID
    $ {command}
    --route-view=projects/-/locations/-/meshes/-/routeViews/$ROUTE_VIEW_ID

  Describe a Route Views for a Gateway

    $ {command} --project=$PROJECT_ID --location=$LOCATION --gateway gateway1
    --route-view $ROUTE_VIEW_ID
    $ {command}
    --route-view=projects/-/locations/-/gateways/-/routeViews/$ROUTE_VIEW_ID
  """

  @staticmethod
  def Args(parser):
    flags.AddRouteViewFlags(parser)
    base.DescribeCommand.Args(parser)

  def Run(self, args):
    name = args.CONCEPTS.route_view.Parse().result.RelativeName()

    return util.GetRouteView(self.ReleaseTrack(), name)
