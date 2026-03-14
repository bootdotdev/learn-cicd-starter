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
"""List keyhandles within a project and location."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import list_pager
from googlecloudsdk.api_lib.cloudkms import base as cloudkms_base
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.kms import flags
from googlecloudsdk.command_lib.kms import resource_args


@base.UniverseCompatible
class List(base.ListCommand):
  """List KeyHandle resources within a project and location.

  Lists all KeyHandle resources within a given project and location.
  Addtionally, can filter the list.

  ## EXAMPLES

  The following command lists a maximum of five KeyHandle resources in the
  location `global`:

    $ {command} --location=global --limit=5

  The following command lists all KeyHandle resources in the location `global`
  that have a resource type selector of `compute.googleapis.com/Instance`:

    $ {command} --location=global
    --resource-type=compute.googleapis.com/Instance
  """

  @staticmethod
  def Args(parser):
    resource_args.AddKmsLocationResourceArgForKMS(parser, True, '--location')
    flags.AddResourceTypeSelectorFlag(parser, True)

    parser.display_info.AddFormat('table(name, kmsKey, resourceTypeSelector)')

  def Run(self, args):
    client = cloudkms_base.GetClientInstance()
    messages = cloudkms_base.GetMessagesModule()
    location_ref = args.CONCEPTS.location.Parse()

    filter_str = f'resource_type_selector="{args.resource_type}"'

    request = messages.CloudkmsProjectsLocationsKeyHandlesListRequest(
        parent=location_ref.RelativeName(), filter=filter_str
    )

    return list_pager.YieldFromList(
        client.projects_locations_keyHandles,
        request,
        field='keyHandles',
        limit=args.limit,
        batch_size_attribute='pageSize',
    )
