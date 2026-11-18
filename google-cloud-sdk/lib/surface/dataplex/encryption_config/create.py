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
"""`gcloud dataplex encryption-config create` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.dataplex import encryption_config
from googlecloudsdk.api_lib.dataplex import util as dataplex_util
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataplex import resource_args
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Create(base.Command):
  """Create a Dataplex encryption config resource.

  An EncryptionConfig is created only for CMEK opted in organizations.
  """

  detailed_help = {
      'EXAMPLES': """\
            To create an EncryptionConfig `default` in organization `test-org-id` at location `us-central1` with key `test-key`, run:
            $ {command} default --location=us-central1 --organization=test-org-id --key='test-key'
            """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddEncryptionConfigResourceArg(parser, 'to create.')
    parser.add_argument(
        '--key',
        required=False,
        help='The KMS key to use for encryption.',
    )

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args):
    encryption_config_ref = args.CONCEPTS.encryption_config.Parse()
    dataplex_client = dataplex_util.GetClientInstance()
    dataplex_client.organizations_locations_encryptionConfigs.Create(
        dataplex_util.GetMessageModule().DataplexOrganizationsLocationsEncryptionConfigsCreateRequest(
            encryptionConfigId=encryption_config_ref.Name(),
            parent=encryption_config_ref.Parent().RelativeName(),
            googleCloudDataplexV1EncryptionConfig=encryption_config.GenerateEncryptionConfigForCreateRequest(
                args
            ),
        )
    )
    # TODO(b/388204419): Add support for waiting for operation to complete.
    log.status.Print(
        'Encryption Config is saved successfully. Please use gcloud describe'
        ' command to check the data encryption status after sometime.'
    )
    return
