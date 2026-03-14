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
"""Command to print an identity token for a specified audience."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from google.auth import exceptions as google_auth_exceptions
from google.oauth2 import gdch_credentials
from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core import requests


def AddCredFileArg(parser):
  parser.add_argument(
      '--cred-file',
      required=True,
      type=str,
      metavar='CRED_FILE',
      help='Path to a credential file.')


def AddAudienceArg(parser):
  parser.add_argument(
      '--audience',
      required=True,
      type=str,
      metavar='AUDIENCE',
      help='Intended recipient of the token. '
           'Currently, only one audience can be specified.')


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class IdentityToken(base.DescribeCommand):
  """Print an identity token for a specified audience.

  ## EXAMPLES

    $ {command} --audience=https://example.com --cred-file=/tmp/cred.json
  """

  @staticmethod
  def Args(parser):
    AddCredFileArg(parser)
    AddAudienceArg(parser)

  def Run(self, args):
    credential = (
        gdch_credentials.ServiceAccountCredentials.from_service_account_file(
            args.cred_file
        )
    )
    credential = credential.with_gdch_audience(args.audience)

    try:
      credential.refresh(requests.GoogleAuthRequest())
    except google_auth_exceptions.RefreshError as e:
      log.error('Failed to refresh credentials: %s', e)
      return None

    log.out.Print(credential.token)
    return None
