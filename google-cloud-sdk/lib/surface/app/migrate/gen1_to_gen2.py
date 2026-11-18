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

"""The gcloud app migrate gen1-to-gen2 command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.app import appengine_api_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.app import migration_util


@base.DefaultUniverseOnly
class Gen1ToGen2(base.Command):
  """Migrate the first-generation App Engine code to be compatible with second-generation runtimes."""

  @staticmethod
  def Args(parser):
    parser.add_argument(
        '--appyaml',
        help=(
            'YAML file for the first-generation App Engine version to be'
            ' migrated.'
        ),
    )
    parser.add_argument(
        '--output-dir',
        required=True,
        help=(
            'The directory where the migrated code for the second-generation'
            ' application will be stored.'
        ),
    )

  def Run(self, args):
    api_client = appengine_api_client.GetApiClientForTrack(self.ReleaseTrack())
    migration_util.Gen1toGen2Migration(api_client, args).StartMigration()
