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
"""Command to describe universe descriptor data."""

from cloudsdk.google.protobuf import json_format
from googlecloudsdk.calliope import base
from googlecloudsdk.core.universe_descriptor import universe_descriptor


@base.Hidden
@base.UniverseCompatible
class Describe(base.Command):
  """Describe universe descriptor data dict in the cache."""

  detailed_help = {
      'EXAMPLES': """\
          To describe an existing universe descriptor with domain `my-universe-domain.com`, run:

            $ {command} my-universe-domain.com
          """,
  }

  @staticmethod
  def Args(parser):
    """Adds args for this command."""
    parser.add_argument(
        'universe_domain',
        help='Universe domain of the universe descriptor to describe.',
    )

  def Run(self, args):
    del self
    universe_descriptor_obj = universe_descriptor.UniverseDescriptor()
    descriptor_json = universe_descriptor_obj.Get(
        args.universe_domain, fetch_if_not_cached=False
    )
    return json_format.MessageToDict(
        descriptor_json, always_print_fields_with_no_presence=True
    )
