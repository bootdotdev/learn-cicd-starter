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
"""Test IAM permissions for a Design Center space."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.design_center import spaces as apis
from googlecloudsdk.api_lib.design_center import utils as api_lib_utils
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.design_center import flags


_DETAILED_HELP = {
    'DESCRIPTION': """ \
        Tests the IAM permissions that a caller has on a Design Center space.

        Returns an empty set of permissions if the space does not exist.

        Note: This operation is designed to be used for building
        permission-aware UIs and command-line tools, not for authorization
        checking. This operation may "fail open" without warning.
        """,
    'EXAMPLES': """ \
        To test if the caller has the `designcenter.spaces.get` and
        `designcenter.spaces.update` permissions on the Space `my-space` in
        project `my-project` and location `us-central1`, run:

          $ {command} my-space --location=us-central1 --project=my-project \
              --permissions=designcenter.spaces.get,designcenter.spaces.update
        """,
    'API REFERENCE': """ \
        This command uses the designcenter/v1alpha API. The full documentation for
        this API can be found at:
        http://cloud.google.com/application-design-center/docs
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
@base.Hidden
class TestIamPermissionsGA(base.Command):
  """Test IAM permissions for a Design Center space."""
  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    flags.AddTestIamPermissionsFlags(parser)
    parser.add_argument(
        '--permissions',
        metavar='PERMISSION',
        type=arg_parsers.ArgList(),
        required=True,
        help='The set of permissions to check for the resource.',
    )

  def Run(self, args):
    client = apis.SpacesClient(release_track=base.ReleaseTrack.GA)
    space_ref = api_lib_utils.GetSpaceRef(args)
    return client.TestIamPermissions(
        space_id=space_ref.RelativeName(),
        permissions=args.permissions,
    )


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class TestIamPermissions(base.Command):
  """Test IAM permissions for a Design Center space."""
  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    flags.AddTestIamPermissionsFlags(parser)
    parser.add_argument(
        '--permissions',
        metavar='PERMISSION',
        type=arg_parsers.ArgList(),
        required=True,
        help='The set of permissions to check for the resource.',
    )

  def Run(self, args):
    client = apis.SpacesClient(release_track=base.ReleaseTrack.ALPHA)
    space_ref = api_lib_utils.GetSpaceRef(args)
    return client.TestIamPermissions(
        space_id=space_ref.RelativeName(),
        permissions=args.permissions,
    )
