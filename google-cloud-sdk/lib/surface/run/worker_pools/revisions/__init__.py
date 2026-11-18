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
"""The gcloud run worker-pools revisions group."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import flags


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Revisions(base.Group):
  """View and manage your Cloud Run WorkerPools revisions.

  This set of commands can be used to view and manage your existing Cloud Run
  WorkerPools revisions.
  """

  detailed_help = {
      'EXAMPLES': """
          To list your existing worker pools revisions, run:

            $ {command} list
      """,
  }
