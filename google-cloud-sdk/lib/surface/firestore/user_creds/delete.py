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
"""Command to delete a user creds for a Firestore Database."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.firestore import user_creds
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.firestore import flags
from googlecloudsdk.core import properties


@base.DefaultUniverseOnly
class Delete(base.Command):
  """Deletes a Cloud Firestore user creds.

  ## EXAMPLES

  To delete user creds 'test-user-creds-id' under
  database testdb.

      $ {command} test-user-creds-id --database='testdb'
  """

  @staticmethod
  def Args(parser):
    """Set args for gcloud firestore user-creds delete."""
    flags.AddDatabaseIdFlag(parser, required=True)
    flags.AddUserCredsIdArg(parser)

  def Run(self, args):
    project = properties.VALUES.core.project.Get(required=True)
    return user_creds.DeleteUserCreds(
        project, args.database, args.user_creds
    )
