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
"""Command group for Dataplex glossary term services."""
from googlecloudsdk.calliope import base


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class GlossaryCategories(base.Group):
  """Manage Dataplex glossary terms.

  Glossary terms are the core of a Dataplex glossary. A glossary term holds a
  rich text description that can be attached to entries or specific columns to
  enrich them.
  """

  category = base.DATA_ANALYTICS_CATEGORY
