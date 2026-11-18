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
"""Create a key handle."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.cloudkms import base as cloudkms_base
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.kms import flags
from googlecloudsdk.core import log
from googlecloudsdk.core import resources


@base.UniverseCompatible
class Create(base.CreateCommand):
  """Create a new KeyHandle.

  Creates a new KeyHandle, triggering the provisioning of a new CryptoKey for
  CMEK use with the given resource type in the configured key project and the
  same location

  ## EXAMPLES

  The following command creates a KeyHandle named `my-key-handle` within the
  location `global` for the resource type `compute.googleapis.com/Disk`:

    $ {command} --key-handle-id=my-key-handle --my-key-handle --location=global
    --resource-type=compute.googleapis.com/Disk

  In case we want to generate a random KeyHandle id, we can use the
  `--generate-key-handle-id` flag instead of the `--key-handle-id` flag.
  """

  @staticmethod
  def Args(parser):

    flags.AddCreateKeyHandleFlags(parser)
    parser.display_info.AddCacheUpdater(flags.KeyHandleCompleter)

  def Run(self, args):
    client = cloudkms_base.GetClientInstance()
    messages = cloudkms_base.GetMessagesModule()

    location_ref = args.CONCEPTS.location.Parse()
    if args.key_handle_id:
      req = messages.CloudkmsProjectsLocationsKeyHandlesCreateRequest(
          parent=location_ref.RelativeName(),
          keyHandleId=args.key_handle_id,
          keyHandle=messages.KeyHandle(resourceTypeSelector=args.resource_type),
      )
    else:
      req = messages.CloudkmsProjectsLocationsKeyHandlesCreateRequest(
          parent=location_ref.RelativeName(),
          keyHandle=messages.KeyHandle(resourceTypeSelector=args.resource_type),
      )

    operation = client.projects_locations_keyHandles.Create(req)
    operation_ref = resources.REGISTRY.ParseRelativeName(
        operation.name, collection='cloudkms.projects.locations.operations'
    )

    created_key_handle = waiter.WaitFor(
        waiter.CloudOperationPoller(
            client.projects_locations_keyHandles,
            client.projects_locations_operations,
        ),
        operation_ref,
        'Waiting for KeyHandle to be created.',
    )

    log.CreatedResource(created_key_handle.name, kind='KeyHandle')
    log.status.Print(
        'The corresponding CryptoKey is: {0}'.format(created_key_handle.kmsKey)
    )
    return created_key_handle
