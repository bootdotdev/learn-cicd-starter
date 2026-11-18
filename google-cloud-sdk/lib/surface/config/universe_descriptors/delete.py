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

"""Command to delete universe descriptor data."""

from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io
from googlecloudsdk.core.universe_descriptor import universe_descriptor


@base.Hidden
@base.UniverseCompatible
class Delete(base.Command):
  """Delete universe descriptor data."""

  @staticmethod
  def Args(parser):
    """Adds args for this command."""
    parser.add_argument(
        'universe_domain',
        help='Universe domain of the descriptor to delete.',
    )

  def Run(self, args):
    del self
    universe_descriptor_obj = universe_descriptor.UniverseDescriptor()
    log.warning(
        'The universe descriptor with universe domain [%s] will be deleted:',
        args.universe_domain,
    )
    console_io.PromptContinue(default=True, cancel_on_no=True)
    try:
      universe_descriptor_obj.DeleteDescriptorFromUniverseDomain(
          args.universe_domain
      )
      log.DeletedResource(
          'Universe descriptor with universe domain [%s]' % args.universe_domain
      )
    except universe_descriptor.UniverseDescriptorError:
      log.warning(
          'No descriptor found for universe domain [%s].', args.universe_domain
      )
      return
