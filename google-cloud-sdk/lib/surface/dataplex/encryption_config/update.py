# -*- coding: utf-8 -*- #
# Copyright 2025 Google Inc. All Rights Reserved.
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
"""`gcloud dataplex encryption-config update` command."""

from googlecloudsdk.api_lib.dataplex import encryption_config
from googlecloudsdk.api_lib.dataplex import util as dataplex_api_util
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataplex import resource_args
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Update(base.UpdateCommand):
  """Update an Encryption Config."""

  detailed_help = {
      'EXAMPLES': """\
          To update EncryptionConfig in organization `123` and location `us-central1`, run:

            $ {command} organizations/123/locations/us-central1/encryptionConfigs/default --enable-metastore-encryption
          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddEncryptionConfigResourceArg(parser, 'to update.')
    parser.add_argument(
        '--enable-metastore-encryption',
        default=False,
        action='store_true',
        help=(
            'Helps user to explicitly enable cmek encryption for dataplex'
            ' metadata storage.'
        ),
    )

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args):
    if not args.enable_metastore_encryption:
      log.status.Print(
          'There is no update for the EncryptionConfig.'
      )
      return
    update_mask = encryption_config.GenerateUpdateMask(args)
    encryption_config_ref = args.CONCEPTS.encryption_config.Parse()
    dataplex_client = dataplex_api_util.GetClientInstance()
    dataplex_client.organizations_locations_encryptionConfigs.Patch(
        dataplex_api_util.GetMessageModule().DataplexOrganizationsLocationsEncryptionConfigsPatchRequest(
            name=encryption_config_ref.RelativeName(),
            updateMask=','.join(update_mask),
            googleCloudDataplexV1EncryptionConfig=encryption_config.GenerateEncryptionConfigForUpdateRequest(
                args
            ),
        ))
    log.status.Print(
        'Successfully updated the Encryption Config. Please use the gcloud '
        'describe to check the latest update of data encryption'
    )
    return
