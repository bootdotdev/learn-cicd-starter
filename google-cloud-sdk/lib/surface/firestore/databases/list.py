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
"""List all Firestore databases under the project."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.firestore import databases
from googlecloudsdk.calliope import base
from googlecloudsdk.core import properties


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class ListAlpha(base.ListCommand):
  """Lists all Firestore databases under the project.

  ## EXAMPLES

  To list all active Firestore databases.

      $ {command}

  To list all Firestore databases including deleted databases.

      $ {command} --show-deleted
  """

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--show-deleted',
        help='Show the deleted databases.',
        action='store_true',
        default=False,
    )

  def ListDatabases(self, show_deleted):
    project = properties.VALUES.core.project.Get(required=True)
    return databases.ListDatabases(project, show_deleted)

  def Run(self, args):
    return self.ListDatabases(args.show_deleted)
