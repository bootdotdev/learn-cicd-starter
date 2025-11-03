# -*- coding: utf-8 -*- #
# Copyright 2022 Google LLC. All Rights Reserved.
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
"""Command to create a login configuration file used to enable browser based sign-in using third-party user identities via gcloud auth login.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import json
import os
import textwrap

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.iam.byoid_utilities import cred_config
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.universe_descriptor import universe_descriptor
from googlecloudsdk.core.util import files


RESOURCE_TYPE = 'login configuration file'
GOOGLE_DEFAULT_CLOUD_WEB_DOMAIN = 'cloud.google'


@base.UniverseCompatible
class CreateLoginConfig(base.CreateCommand):
  """Create a login configuration file to enable sign-in via a web-based authorization flow using Workforce Identity Federation.

  This command creates a configuration file to enable browser based
  third-party sign in with Workforce Identity Federation through
  `gcloud auth login --login-config=/path/to/config.json`.
  """

  detailed_help = {
      'EXAMPLES':
          textwrap.dedent("""\
          To create a login configuration for your project, run:

            $ {command} locations/global/workforcePools/$WORKFORCE_POOL_ID/providers/$PROVIDER_ID --output-file=login-config.json
          """),
  }

  @classmethod
  def Args(cls, parser):
    # Required args.
    parser.add_argument(
        'audience', help='Workforce pool provider resource name.'
    )
    parser.add_argument(
        '--output-file',
        help='Location to store the generated login configuration file.',
        required=True,
    )
    # Optional args.
    parser.add_argument(
        '--activate',
        action='store_true',
        default=False,
        help=(
            'Sets the property `auth/login_config_file` to the created login'
            ' configuration file. Calling `gcloud auth login` will'
            ' automatically use this login configuration unless it is'
            ' explicitly unset.'
        ),
    )
    parser.add_argument(
        '--enable-mtls',
        help='Use mTLS for STS endpoints.',
        action='store_true',
        hidden=True,
    )
    parser.add_argument(
        '--universe-domain',
        help='The universe domain.',
        hidden=True,
    )
    parser.add_argument(
        '--universe-cloud-web-domain',
        help='The universe cloud web domain.',
        hidden=True,
    )

  def Run(self, args):
    # Take universe domains into account.
    universe_domain_property = properties.VALUES.core.universe_domain

    universe_domain = universe_domain_property.Get()
    # Universe_domain arg takes precedence over the configuration.
    if getattr(args, 'universe_domain', None):
      universe_domain = args.universe_domain

    # Don't use universe descriptor for GDU as there is a potential edge case
    # that will result in the cloud web domain not being retrievable.
    # TODO(b/368357376): Remove once the edge case is fixed.
    if universe_domain == universe_domain_property.default:
      universe_cloud_web_domain = GOOGLE_DEFAULT_CLOUD_WEB_DOMAIN
    # Hidden attribute. Should not be used, but check just in case.
    elif getattr(args, 'universe_cloud_web_domain', None):
      universe_cloud_web_domain = args.universe_cloud_web_domain
    else:
      universe_cloud_web_domain = (
          universe_descriptor.UniverseDescriptor()
          .Get(universe_domain)
          .cloud_web_domain
      )

    enable_mtls = getattr(args, 'enable_mtls', False)
    token_endpoint_builder = cred_config.StsEndpoints(
        enable_mtls=enable_mtls, universe_domain=universe_domain
    )
    output = {
        'universe_domain': universe_domain,
        'universe_cloud_web_domain': universe_cloud_web_domain,
        'type': 'external_account_authorized_user_login_config',
        'audience': '//iam.googleapis.com/' + args.audience,
        'auth_url': 'https://auth.{cloud_web_domain}/authorize'.format(
            cloud_web_domain=universe_cloud_web_domain
        ),
        'token_url': token_endpoint_builder.oauth_token_url,
        'token_info_url': token_endpoint_builder.token_info_url,
    }

    files.WriteFileContents(args.output_file, json.dumps(output, indent=2))
    log.CreatedResource(args.output_file, RESOURCE_TYPE)

    if args.activate:
      properties.PersistProperty(
          properties.VALUES.auth.login_config_file,
          os.path.abspath(args.output_file),
      )
