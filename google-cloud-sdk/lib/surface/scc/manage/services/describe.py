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
"""Command to get an SCC service."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.scc.manage.services import clients
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scc.manage import flags
from googlecloudsdk.command_lib.scc.manage import parsing


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.ALPHA)
class Describe(base.DescribeCommand):
  """Get the details of a Security Command Center service.

  Get the details of a Security Command Center service. It
  resolves INHERITED enablement states
  to ENABLED or DISABLED for services at ancestor levels. For example, if
  the service is enabled
  at the ancestor level, services for all child resources will have the
  enablement state set to
  ENABLED.

  ## EXAMPLES

  To get the details of a Security Command Center service with name
  `sha` for organization `123`, run:

    $ {command} sha --organization=123

  To get the details of a Security Command Center service with name
  `sha` for folder `456`, run:

    $ {command} sha --folder=456

  To get the details of a Security Command Center service with ID
  `sha` for project `789`, run:

    $ {command} sha --project=789

  You can also specify the parent more generally:

    $ {command} sha --parent=organizations/123

  To get the details of modules, `[ABC, DEF]` of a Security Command
  Center service with name `sha` for organization `123`, run:

    $ {command} sha --module-list=[ABC, DEF] --organization=123
  """

  @staticmethod
  def Args(parser):
    flags.CreateServiceNameArg().AddToParser(parser)
    flags.CreateParentFlag(required=True).AddToParser(parser)
    flags.CreateModuleList().AddToParser(parser)

  def Run(self, args):
    name = parsing.GetServiceNameFromArgs(args)
    module_list = parsing.GetModuleListFromArgs(args)
    client = clients.SecurityCenterServicesClient()

    response = client.Get(name)

    if not module_list:
      return response
    else:
      filtered_response = [
          module_value
          for module_value in response.modules.additionalProperties
          if module_value.key in module_list
      ]
      return filtered_response
