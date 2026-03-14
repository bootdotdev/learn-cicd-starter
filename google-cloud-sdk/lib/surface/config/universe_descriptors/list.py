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

"""Command to list cached universe descriptors."""

import sqlite3

from googlecloudsdk.calliope import base
from googlecloudsdk.core import config
from googlecloudsdk.core.universe_descriptor import universe_descriptor


@base.UniverseCompatible
class List(base.ListCommand):
  """List cached universe descriptors."""

  @staticmethod
  def Args(parser):
    base.PAGE_SIZE_FLAG.RemoveFromParser(parser)
    base.URI_FLAG.RemoveFromParser(parser)
    table_format = """table(
      universe_domain,
      universe_short_name,
      project_prefix,
      authentication_domain,
      cloud_web_domain,
      version)
    """
    parser.display_info.AddFormat(table_format)

  def Run(self, unused_args):
    config_universe_domains = universe_descriptor.GetAllConfigUniverseDomains()
    config_store = config.GetConfigStore(
        universe_descriptor.CONFIG_CACHE_DESCRIPTOR_DATA_TABLE_NAME
    )
    for universe_domain in config_universe_domains:
      try:
        yield config_store.GetJSON(universe_domain)
      except sqlite3.Error:
        pass
