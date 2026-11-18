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
"""List deployments command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_security.security_profiles import mirroring_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security import sp_flags

DETAILED_HELP = {
    'DESCRIPTION': """
          List Custom Mirroring Security Profiles.

          For more examples, refer to the EXAMPLES section below.

        """,
    'EXAMPLES': """
            To list Custom Mirroring security profiles in an organization, run:

            $ {command} --organization=12345 --location=global

        """,
}

_FORMAT = """\
table(
    name.scope("securityProfiles"):label=ID,
    custom_mirroring_profile.mirroring_endpoint_group
)
"""


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class List(base.ListCommand):
  """List Custom Mirroring Security Profiles."""

  detailed_help = DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    parser.display_info.AddFormat(_FORMAT)
    parser.display_info.AddUriFunc(sp_flags.MakeGetUriFunc(cls.ReleaseTrack()))
    sp_flags.AddLocationResourceArg(
        parser, 'Parent resource for the list operation.'
    )

  def Run(self, args):
    client = mirroring_api.Client(self.ReleaseTrack())

    parent_ref = args.CONCEPTS.location.Parse()

    return client.ListCustomMirroringProfiles(
        parent_ref.RelativeName(), page_size=args.page_size
    )
