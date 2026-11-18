# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
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
"""gcloud service-extensions wasm-plugins create command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.service_extensions import wasm_plugin_api
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.command_lib.service_extensions import flags
from googlecloudsdk.command_lib.service_extensions import util
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


def _GetLogConfig(args, api_version):
  """Converts the dict representation of the log_config to proto.

  Args:
    args: args with log_level parsed ordered dict. If log-level flag is set,
      enable option should also be set.
    api_version: API version (e.g. v1apha1)

  Returns:
    a value of messages.WasmPluginLogConfig or None,
    if log-level flag were not provided.
  """

  if args.log_config is None:
    return None
  return util.GetLogConfig(args.log_config[0], api_version)


def GetPluginConfigData(args):
  return args.plugin_config or args.plugin_config_file


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Create(base.CreateCommand):
  """Create a `WasmPlugin` resource."""

  detailed_help = {
      'DESCRIPTION': textwrap.dedent("""\
          Create a new `WasmPlugin` resource.
      """),
      'EXAMPLES': textwrap.dedent("""\
          To create a `WasmPlugin` called `my-plugin`, together with a new
          version called `v1`, and set it as main, run:

          $ {command} my-plugin --main-version=v1
          --image=...-docker.pkg.dev/my-project/repository/container:tag
          """),
  }

  @classmethod
  def Args(cls, parser):
    api_version = util.GetApiVersion(cls.ReleaseTrack())
    flags.AddWasmPluginResource(
        parser=parser,
        api_version=api_version,
        message='The ID of the `WasmPlugin` resource to create.',
    )

    base.ASYNC_FLAG.AddToParser(parser)
    labels_util.AddCreateLabelsFlags(parser)
    flags.AddDescriptionFlag(parser)
    flags.AddLogConfigFlag(parser, api_version)

    flags.AddWasmPluginVersionArgs(
        parser=parser,
        version_message=(
            'ID of the `WasmPluginVersion` resource that will be created for '
            'that `WasmPlugin` and that will be set as the current '
            'main version.'
        ),
    )

  def Run(self, args):
    api_version = util.GetApiVersion(self.ReleaseTrack())
    if args.main_version is None:
      raise calliope_exceptions.RequiredArgumentException(
          '--main-version', 'Flag --main-version is mandatory.'
      )
    if not args.main_version:
      raise calliope_exceptions.RequiredArgumentException(
          '--main-version', 'Flag --main-version cannot be empty.'
      )
    if args.image is None:
      raise calliope_exceptions.RequiredArgumentException(
          '--image', 'Flag --image is mandatory.'
      )

    wp_client = wasm_plugin_api.Client(self.ReleaseTrack())

    wasm_plugin_ref = args.CONCEPTS.wasm_plugin.Parse()
    labels = labels_util.ParseCreateArgs(
        args, wp_client.messages.WasmPlugin.LabelsValue
    )
    log_config = _GetLogConfig(args, api_version)

    versions = wp_client.PrepareVersionDetailsForSingleVersion(
        args.main_version,
        args.image,
        GetPluginConfigData(args),
        args.plugin_config_uri,
    )

    op_ref = wp_client.CreateWasmPlugin(
        parent=wasm_plugin_ref.Parent().RelativeName(),
        name=wasm_plugin_ref.Name(),
        description=args.description,
        labels=labels,
        log_config=log_config,
        main_version=args.main_version,
        versions=versions,
    )
    log.status.Print(
        'Create request issued for: [{}]'.format(wasm_plugin_ref.Name())
    )

    if args.async_:
      log.status.Print('Check operation [{}] for status.'.format(op_ref.name))
      return op_ref

    result = wp_client.WaitForOperation(
        operation_ref=op_ref,
        message='Waiting for operation [{}] to complete'.format(op_ref.name),
    )

    log.status.Print(
        'Created WasmPlugin [{}] with WasmPluginVersion [{}].'.format(
            wasm_plugin_ref.Name(), args.main_version
        )
    )

    return result
