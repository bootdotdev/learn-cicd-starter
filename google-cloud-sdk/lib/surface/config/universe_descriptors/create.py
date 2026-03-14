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

"""Command to create a universe descriptor data entry in the cache."""

from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core.universe_descriptor import universe_descriptor


@base.UniverseCompatible
class Create(base.Command):
  """Create a new universe descriptor data entry."""

  @staticmethod
  def Args(parser):
    """Adds args for this command."""
    parser.add_argument(
        'universe_domain',
        help='Universe domain of the universe descriptor to add to the cache.',
    )

  def Run(self, args):
    del self
    universe_descriptor_obj = universe_descriptor.UniverseDescriptor()
    try:
      universe_descriptor_obj.Get(
          args.universe_domain, fetch_if_not_cached=False
      )
    except universe_descriptor.UniverseDescriptorError:
      pass
    else:
      log.error(
          'Universe descriptor with universe domain [%s] already cached.',
          args.universe_domain,
      )
      return

    universe_descriptor_obj.UpdateDescriptorFromUniverseDomain(
        args.universe_domain
    )
    log.status.Print(
        'Universe descriptor with universe domain [%s] cached.'
        % args.universe_domain,
    )
