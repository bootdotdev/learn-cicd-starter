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
"""The gcloud firestore bulk delete command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.firestore import bulk_delete
from googlecloudsdk.api_lib.firestore import operations
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.firestore import flags
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class BulkDelete(base.Command):
  """bulk delete Cloud Firestore documents."""

  detailed_help = {'EXAMPLES': """\
          To bulk delete a specific set of collections groups asynchronously, run:

            $ {command} --collection-ids='specific collection group1','specific collection group2' --async

          To bulk delete all collection groups from certain namespace, run:

            $ {command} --namespace-ids='specific namespace id'
      """}

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.AddCollectionIdsFlag(parser)
    flags.AddNamespaceIdsFlag(parser)
    flags.AddDatabaseIdFlag(parser)
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    project = properties.VALUES.core.project.Get(required=True)
    message = (
        'You are about to bulk delete data from namespace ids:{} and'
        ' collection ids: {}'.format(args.namespace_ids, args.collection_ids)
    )
    console_io.PromptContinue(
        message=message, throw_if_unattended=True, cancel_on_no=True
    )

    response = bulk_delete.BulkDelete(
        project,
        args.database,
        namespace_ids=args.namespace_ids,
        collection_ids=args.collection_ids,
    )

    if not args.async_:
      operations.WaitForOperation(response)

    return response
