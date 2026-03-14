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
"""The gcloud run presets list command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import pkgutil

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run.printers import presets_printer
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import yaml


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class List(base.ListCommand):
  """List available Cloud Run presets. Currently only available in alpha."""

  detailed_help = {
      'DESCRIPTION': """
          {description}
      """,
      'EXAMPLES': """
          To list all available presets, run:

            $ {command}
      """,
  }

  @classmethod
  def CommonArgs(cls, parser):
    """Adds the display format for the command output."""
    parser.display_info.AddFormat('table(name, category(), description)')
    parser.display_info.AddTransforms({'category': _TransformCategory})

  @classmethod
  def Args(cls, parser):
    cls.CommonArgs(parser)

  def Run(self, _):
    """Reads a Preset YAML file and returns its contents for display."""
    try:
      # TODO(b/414798340): Modify this when PresetMetadata design is finalized.
      presets_yaml_contents = pkgutil.get_data(
          'googlecloudsdk.command_lib.run', 'presets.yaml')
      presets_data = yaml.load(presets_yaml_contents)

    except IOError:
      raise exceptions.Error('Presets file not found.')
    return presets_data['presets']


def _TransformCategory(r):
  return presets_printer.PRESETS_ENUM_MAP.get(r.get('category'))
