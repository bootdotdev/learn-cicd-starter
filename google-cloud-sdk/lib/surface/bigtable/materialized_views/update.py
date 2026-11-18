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
"""Bigtable materialized views update command."""

import textwrap
from typing import Optional

from apitools.base.py import exceptions
from googlecloudsdk.api_lib.bigtable import materialized_views
from googlecloudsdk.api_lib.bigtable import util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import parser_arguments
from googlecloudsdk.calliope import parser_extensions
from googlecloudsdk.command_lib.bigtable import arguments
from googlecloudsdk.core import log
from googlecloudsdk.core import resources
from googlecloudsdk.generated_clients.apis.bigtableadmin.v2 import bigtableadmin_v2_messages


HttpError = exceptions.HttpError


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.GA, base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA
)
class UpdateMaterializedView(base.UpdateCommand):
  """Update a Bigtable materialized view."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          To update a materialized view, run:

            $ {command} my-materialized-view-id --instance=my-instance-id --deletion-protection=true
          """),
  }

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor) -> None:
    arguments.AddMaterializedViewResourceArg(parser, 'to update')
    arguments.ArgAdder(parser).AddDeletionProtection(True).AddAsync()

  def _UpdateMaterializedView(
      self,
      materialized_view_ref: resources.Resource,
      args: parser_extensions.Namespace,
  ) -> bigtableadmin_v2_messages.MaterializedView:
    """Updates a materialized view with the given arguments.

    Args:
      materialized_view_ref: A resource reference of the new materialized view.
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Updated materialized view resource object.
    """
    return materialized_views.Update(
        materialized_view_ref, args.deletion_protection
    )

  def Run(
      self, args: parser_extensions.Namespace
  ) -> Optional[bigtableadmin_v2_messages.MaterializedView]:
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Updated resource.
    """
    materialized_view_ref = args.CONCEPTS.materialized_view.Parse()
    operation = self._UpdateMaterializedView(materialized_view_ref, args)
    if not args.async_:
      operation_ref = util.GetOperationRef(operation)
      return util.AwaitMaterializedView(
          operation_ref,
          'Updating materialized view {0}'.format(materialized_view_ref.Name()),
      )

    log.UpdatedResource(
        materialized_view_ref.Name(),
        kind='materialized view',
        is_async=args.async_,
    )
    return None
