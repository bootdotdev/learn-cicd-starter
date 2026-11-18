# -*- coding: utf-8 -*- #
# Copyright 2025 Google LLC. All Rights Reserved.
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
"""`gcloud scheduler cmek-config update` command."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from googlecloudsdk.api_lib import scheduler
from googlecloudsdk.api_lib.scheduler import cmek_config
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scheduler import flags
from googlecloudsdk.command_lib.scheduler import parsers
from googlecloudsdk.generated_clients.apis.cloudscheduler.v1 import cloudscheduler_v1_messages as messages


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class UpdateCmekConfig(base.Command):
  """Update CMEK configuration for Cloud Scheduler in the specified location."""

  detailed_help = {
      'DESCRIPTION': """\
          {description}
          """,
      'EXAMPLES': """\
          To update a CMEK config:
              $ {command} --location=my-location --kms-location=europe-southwest1 --kms-project=new-kms-project --kms-keyring=kms-keyring2 --kms-key=crypto-key2
         """,
  }

  @staticmethod
  def Args(parser):
    flags.UpdateAndClearCmekConfigResourceFlag(parser)

  def Run(self, args):
    api = scheduler.GetApiAdapter(self.ReleaseTrack())
    cmek_config_client = api.cmek_config
    if args.clear_kms_key:
      # When clearing, we only need to have location and _PROJECT()
      project_id, location_id = parsers.ParseKmsClearArgs(args)
      if location_id is None or project_id is None:
        raise cmek_config.RequiredFieldsMissingError(
            'The location or project are undefined.'
            ' Please set these flags properly.'
        )
      full_kms_key_name = ''
    else:
      project_id, location_id, full_kms_key_name = parsers.ParseKmsUpdateArgs(
          args
      )
      # When updating, flags combination must be set properly. Either a full KMS
      # key name is provided, or all of the flags are provided.
      if full_kms_key_name is None or location_id is None or project_id is None:
        raise cmek_config.RequiredFieldsMissingError(
            'One or more of the --kms-key-name, --kms-keyring, --location, or'
            ' --project are invalid. Please set these flags properly or make'
            ' sure the full KMS key name is valid. (args: kms_key={},'
            ' location={}, project={})'.format(
                full_kms_key_name, location_id, project_id
            )
        )

    config = messages.CmekConfig()
    config.name = f'projects/{project_id}/locations/{location_id}/cmekConfig'
    config.kmsKeyName = full_kms_key_name
    update_cmek_config = cmek_config_client.UpdateCmekConfig(
        project_id, location_id, config
    )
    return update_cmek_config
