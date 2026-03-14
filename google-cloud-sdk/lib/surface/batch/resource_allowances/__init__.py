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

"""The resource allowances command group for the Batch API CLI."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base


DETAILED_HELP = {
    'DESCRIPTION': """
        The gcloud batch resource allowances command group lets you create, describe, list and delete
        Batch resource allowances.

        With Batch, you can utilize the fully managed service to schedule, queue, and
        execute batch resource allowances  on Google's infrastructure.

        For more information about Batch, see the
        [Batch overview](https://cloud.google.com/batch)
        and the
        [Batch documentation](https://cloud.google.com/batch/docs/).
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class ResourceAllowances(base.Group):
  """Manage Batch resource allowance resources."""

  detailed_help = DETAILED_HELP

  category = base.BATCH_CATEGORY
