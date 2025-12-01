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
"""Update Command for the Resource Manager - Tags Bindings CLI."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import urllib.parse

from googlecloudsdk.api_lib.resource_manager import tags
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.resource_manager import endpoint_utils as endpoints
from googlecloudsdk.command_lib.resource_manager import tag_arguments as arguments
from googlecloudsdk.command_lib.resource_manager import tag_utils


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Update(base.Command):
  """Updates TagBindings bound to the specified resource."""

  @staticmethod
  def Args(parser):
    arguments.AddUpdateResourceNameArgToParser(
        parser,
        message="Full resource name of the resource to attach to the tagValue.",
    )
    arguments.AddLocationArgToParser(
        parser,
        (
            "Region or zone of the resource to bind to the TagValue. This "
            "field is not required if the resource is a global resource like "
            "projects, folders and organizations."
        ),
    )
    arguments.UpdateTagGroup(parser)

  def Run(self, args):
    messages = tags.TagMessages()

    location = args.location if args.IsSpecified("location") else None

    resource_name = tag_utils.GetCanonicalResourceName(
        args.resource_name, location, base.ReleaseTrack.ALPHA
    )

    if location is None:
      tag_binding_collection_name = (
          "locations/global"
          + "/tagBindingCollections/"
          + urllib.parse.quote(resource_name, safe="")
      )
    else:
      tag_binding_collection_name = (
          "locations/"
          + location
          + "/tagBindingCollections/"
          + urllib.parse.quote(resource_name, safe="")
      )

    list_req = (
        messages.CloudresourcemanagerLocationsTagBindingCollectionsGetRequest(
            name=tag_binding_collection_name
        )
    )
    with endpoints.CrmEndpointOverrides(location):
      list_service = tags.TagBindingsCollectionService()
      original = list_service.Get(list_req)

    # Initialize update mask to "*" to make a put request. We can update it
    # further to support patch requests.
    update_mask = "*"

    tags_map_to_update = tag_utils.ParseTagGroup(args, original)
    tag_bindings = messages.TagBindingCollection.TagsValue()

    for tag_key, tag_value in tags_map_to_update.items():
      additional_property = (
          messages.TagBindingCollection.TagsValue.AdditionalProperty(
              key=tag_key, value=tag_value
          )
      )
      tag_bindings.additionalProperties.append(additional_property)
      # additional_property is a
      # TagBindingCollection.TagsValue.AdditionalProperty

    tag_binding_collection = messages.TagBindingCollection(
        etag=original.etag,
        name=tag_binding_collection_name,
        fullResourceName=resource_name,
        tags=tag_bindings,
    )

    update_req = (
        messages.CloudresourcemanagerLocationsTagBindingCollectionsPatchRequest(
            name=tag_binding_collection_name,
            tagBindingCollection=tag_binding_collection,
            updateMask=update_mask,
        )
    )

    with endpoints.CrmEndpointOverrides(location):
      service = tags.TagBindingsCollectionService()
      op = service.Patch(update_req)

    return op
