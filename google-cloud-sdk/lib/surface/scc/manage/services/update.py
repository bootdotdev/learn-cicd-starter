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
"""Command to update an SCC service."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.scc.manage.services import clients
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scc.manage import flags
from googlecloudsdk.command_lib.scc.manage import parsing
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.ALPHA)
class Update(base.Command):
  """Update a Security Command Center service.

  Update the enablement state of the Security Center service and its
  corresponding modules for the specified folder, project or organization.

  ## EXAMPLES

  To update a Security Center Service with name `sha` for organization 123, run:

      $ {command} sha
          --organization=organizations/123 --enablement-state="ENABLED"

  To update a Security Center Service with name `sha` and its modules for
  organization 123, run:

      $ {command} sha
          --organization=organizations/123 --enablement-state="ENABLED"
          --module-config-file=module_config.yaml

  To validate an update of Security Center Service with name `sha` and its
  modules for organization 123, run:

      $ {command} sha
          --organization=organizations/123 --enablement-state="ENABLED"
          --module-config-file=module_config.yaml --validate-only
  """

  @staticmethod
  def Args(parser):
    flags.CreateServiceNameArg().AddToParser(parser)
    flags.CreateParentFlag(required=True).AddToParser(parser)
    flags.CreateValidateOnlyFlag(required=False).AddToParser(parser)
    flags.CreateServiceUpdateFlags(
        required=True,
        file_type='JSON or YAML',
    ).AddToParser(parser)

  def Run(self, args):
    name = parsing.GetServiceNameFromArgs(args)

    validate_only = args.validate_only
    module_config = parsing.GetModuleConfigValueFromArgs(
        args.module_config_file
    )
    enablement_state = parsing.GetServiceEnablementStateFromArgs(
        args.enablement_state
    )
    update_mask = parsing.CreateUpdateMaskFromArgsForService(args)

    if not validate_only:
      console_io.PromptContinue(
          message=(
              'Are you sure you want to update the Security Center Service'
              ' {}?\n'.format(name)
          ),
          cancel_on_no=True,
      )
    client = clients.SecurityCenterServicesClient()

    return client.Update(
        name=name,
        validate_only=validate_only,
        module_config=module_config,
        enablement_state=enablement_state,
        update_mask=update_mask,
    )
