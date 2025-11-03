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
"""Fetch the IAM policy for a space."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.design_center import spaces as apis
from googlecloudsdk.api_lib.design_center import utils as api_lib_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.design_center import flags


_DETAILED_HELP = {
    'DESCRIPTION': """ \
        Get the IAM policy for a Design Center space.

        Returns an empty policy if the space does not have
        an existing IAM policy set.
        """,
    'EXAMPLES': """ \
        To get the space IAM policy for the Space `my-space` in
        project `my-project` in location `us-central1`, run:

          $ {command} my-space --location=us-central1 --project=my-project
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
class GetIamPolicyGA(base.ListCommand):
  """Get the IAM policy for a Design Center space.

  Returns an empty policy if the space does not have
  an existing IAM policy set.
  """
  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    flags.AddGetIamPolicyFlags(parser)
    base.URI_FLAG.RemoveFromParser(parser)

  def Run(self, args):
    client = apis.SpacesClient(release_track=base.ReleaseTrack.GA)
    space_ref = api_lib_utils.GetSpaceRef(args)
    return client.GetIamPolicy(space_id=space_ref.RelativeName())


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class GetIamPolicy(base.ListCommand):
  """Get the IAM policy for a Design Center space.

  Returns an empty policy if the space does not have
  an existing IAM policy set.
  """
  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    flags.AddGetIamPolicyFlags(parser)
    base.URI_FLAG.RemoveFromParser(parser)

  def Run(self, args):
    client = apis.SpacesClient(release_track=base.ReleaseTrack.ALPHA)
    space_ref = api_lib_utils.GetSpaceRef(args)
    return client.GetIamPolicy(space_id=space_ref.RelativeName())
