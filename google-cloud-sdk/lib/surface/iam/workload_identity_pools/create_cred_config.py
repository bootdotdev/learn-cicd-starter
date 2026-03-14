# -*- coding: utf-8 -*- #
# Copyright 2020 Google LLC. All Rights Reserved.
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
"""Command to create a configuration file to allow authentication from 3rd party sources."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.iam import flags
from googlecloudsdk.command_lib.iam.byoid_utilities import cred_config


@base.UniverseCompatible
class CreateCredConfig(base.CreateCommand):
  """Create a configuration file for generated credentials.

  This command creates a configuration file to allow access to authenticated
  Google Cloud actions from a variety of external accounts.
  """

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          To create a file-sourced credential configuration for your project, run:

            $ {command} projects/$PROJECT_NUMBER/locations/$REGION/workloadIdentityPools/$WORKLOAD_POOL_ID/providers/$PROVIDER_ID --service-account=$EMAIL --credential-source-file=$PATH_TO_OIDC_ID_TOKEN --output-file=credentials.json

          To create a URL-sourced credential configuration for your project, run:

            $ {command} projects/$PROJECT_NUMBER/locations/$REGION/workloadIdentityPools/$WORKLOAD_POOL_ID/providers/$PROVIDER_ID --service-account=$EMAIL --credential-source-url=$URL_FOR_OIDC_TOKEN --credential-source-headers=Key=Value --output-file=credentials.json

          To create an executable-source credential configuration for your project, run the following command:

            $ {command} locations/$REGION/workforcePools/$WORKFORCE_POOL_ID/providers/$PROVIDER_ID --executable-command=$EXECUTABLE_COMMAND --executable-timeout-millis=30000 --executable-output-file=$CACHE_FILE --output-file=credentials.json

          To create an AWS-based credential configuration for your project, run:

            $ {command} projects/$PROJECT_NUMBER/locations/$REGION/workloadIdentityPools/$WORKLOAD_POOL_ID/providers/$PROVIDER_ID --service-account=$EMAIL --aws --enable-imdsv2 --output-file=credentials.json

          To create an Azure-based credential configuration for your project, run:

            $ {command} projects/$PROJECT_NUMBER/locations/$REGION/workloadIdentityPools/$WORKLOAD_POOL_ID/providers/$PROVIDER_ID --service-account=$EMAIL --azure --app-id-uri=$URI_FOR_AZURE_APP_ID --output-file=credentials.json

          To create an X.509 certificate-based credential configuration for your project, run:

            $ {command} projects/$PROJECT_NUMBER/locations/$REGION/workloadIdentityPools/$WORKLOAD_POOL_ID/providers/$PROVIDER_ID --service-account=$EMAIL --credential-cert-path=$PATH_TO_CERTIFICATE_FILE --credential-cert-private-key-path=$PATH_TO_PRIVATE_KEY_FILE --output-file=credentials.json

          To use the resulting file for any of these commands, set the GOOGLE_APPLICATION_CREDENTIALS environment variable to point to the generated file
          """),
  }

  @classmethod
  def Args(cls, parser):
    # Add args common between workload and workforce.
    flags.AddCommonByoidCreateConfigFlags(
        parser, cred_config.ConfigType.WORKLOAD_IDENTITY_POOLS)

    parser.add_argument(
        'audience',
        help='The workload identity pool provider fully qualified identifier.',
    )

    credential_types = parser.add_group(
        mutex=True, required=True, help='Credential types.'
    )
    credential_types.add_argument(
        '--credential-source-file',
        help='Location of the credential source file.',
    )
    credential_types.add_argument(
        '--credential-source-url', help='URL to obtain the credential from.'
    )
    credential_types.add_argument(
        '--executable-command',
        help=(
            'The full command to run to retrieve the credential. Must be an'
            ' absolute path for the program including arguments.'
        ),
    )
    credential_types.add_argument('--aws', help='Use AWS.', action='store_true')
    credential_types.add_argument(
        '--azure', help='Use Azure.', action='store_true'
    )
    credential_types.add_argument(
        '--credential-cert-path', help='Path of the X.509 certificate file.'
    )

    # Optional args.
    parser.add_argument(
        '--subject-token-type',
        help='The type of token being used for authorization. '
        + 'This defaults to urn:ietf:params:oauth:token-type:jwt.',
    )
    parser.add_argument(
        '--app-id-uri',
        help='The custom Application ID URI for the Azure access token.',
    )
    parser.add_argument(
        '--enable-imdsv2',
        help=(
            'Adds the AWS IMDSv2 session token Url to the credential source to'
            ' enforce the AWS IMDSv2 flow.'
        ),
        action='store_true',
    )

    certificate_args = parser.add_group(
        help='Arguments for an X.509 certificate type credential source.'
    )
    certificate_args.add_argument(
        '--credential-cert-private-key-path',
        help='Path of the X.509 private key file.',
        required=True,
    )
    certificate_args.add_argument(
        '--credential-cert-configuration-output-file',
        help=(
            'Path for the certificate configuration file. If specified, a'
            ' certificate configuration file will be created at the specified'
            ' path. If not specified, the certificate configuration will be'
            ' created at the default gcloud location.'
        ),
    )
    certificate_args.add_argument(
        '--credential-cert-trust-chain-path',
        help=(
            'Path for the trust chain file. A trust chain file is required'
            ' if there are intermediate certificates in the certificate chain'
            ' in between the root certificate stored in the workload identity'
            ' pool provider trust store. This trust chain file should be a list'
            ' of PEM certificates, with the leaf certificate at the top.'
        ),
    )

    parser.add_argument(
        '--sts-location',
        help=(
            'The location to use for the Security Token Service token '
            'endpoint. For example, specifying `us-central1` will configure '
            'the client to use the regional endpoint '
            '`sts.us-central1.rep.googleapis.com`. If not specified, the '
            'global endpoint `sts.googleapis.com` is used.'
        ),
    )

  def _ValidateArgs(self, args):
    if args.enable_imdsv2 and not args.aws:
      raise exceptions.ConflictingArgumentsException(
          '--enable-imdsv2 can be used only for AWS credential types'
      )
    if args.credential_cert_private_key_path and not args.credential_cert_path:
      raise exceptions.ConflictingArgumentsException(
          '--credential-cert-private-key-path can be used only for X.509'
          ' certificate credential types'
      )
    if (args.sts_location and args.sts_location != 'global') and (
        args.credential_cert_path
        or args.credential_cert_private_key_path
        or args.credential_cert_trust_chain_path
    ):
      # X.509 federation is not GA-ed on REP/locational endpoints.
      raise exceptions.ConflictingArgumentsException(
          'Workload Identity Federation with X.509 certificates is not'
          ' supported on locational Security Token Service endpoints.'
      )

  def Run(self, args):
    self._ValidateArgs(args)
    cred_config.create_credential_config(
        args, cred_config.ConfigType.WORKLOAD_IDENTITY_POOLS
    )
