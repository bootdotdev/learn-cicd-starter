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
"""Describe the AutokeyConfig of a folder."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.cloudkms import base as cloudkms_base
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.kms import flags
from googlecloudsdk.command_lib.kms import parsing


@base.UniverseCompatible
class Describe(base.DescribeCommand):
  r"""Updates the AutokeyConfig for a folder.

  {command} can be used to update the AutokeyConfig of a folder.

  ## EXAMPLES

  The following command updates the AutokeyConfig for the folder mentioned in
  the config.yaml file:

  $ {command} config.yaml
  """

  @staticmethod
  def Args(parser):
    flags.AddAutokeyConfigFileFlag(parser)

  def Run(self, args):
    client = cloudkms_base.GetClientInstance()
    messages = cloudkms_base.GetMessagesModule()

    name, key_project, etag = parsing.ReadAutokeyConfigFromConfigFile(
        args.CONFIG_FILE
    )
    if not etag:
      return client.folders.UpdateAutokeyConfig(
          messages.CloudkmsFoldersUpdateAutokeyConfigRequest(
              autokeyConfig=messages.AutokeyConfig(
                  name=name, keyProject=key_project
              ),
              name=name,
              updateMask="keyProject",
          ),
      )
    return client.folders.UpdateAutokeyConfig(
        messages.CloudkmsFoldersUpdateAutokeyConfigRequest(
            autokeyConfig=messages.AutokeyConfig(
                name=name, keyProject=key_project, etag=etag
            ),
            name=name,
            updateMask="keyProject",
        )
    )
