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
"""Command for deleting multi-MIGs."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.api_lib.compute.multi_migs import utils as api_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.multi_migs import utils as flags


DETAILED_HELP = {
    'EXAMPLES': """\
      To delete a multi-MIG with the name 'example-multimig' run:

        $ {command} example-multimig
      """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class Delete(base.DeleteCommand):
  """Delete a multi-MIG.

  *{command}* deletes a multi-MIG.
  """

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    flags.AddMultiMigNameArgToParser(
        parser, base.ReleaseTrack.BETA.name.lower()
    )

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    multi_mig_ref = args.CONCEPTS.multi_mig.Parse()

    utils.PromptForDeletion([multi_mig_ref])

    return api_utils.Delete(client, multi_mig_ref)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class DeleteAlpha(Delete):
  """Delete a multi-MIG."""

  @classmethod
  def Args(cls, parser):
    flags.AddMultiMigNameArgToParser(
        parser, base.ReleaseTrack.ALPHA.name.lower()
    )
