# -*- coding: utf-8 -*- #
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""List command for the Tag Manager - Tag Bindings CLI."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import urllib.parse

from apitools.base.py import list_pager
from googlecloudsdk.api_lib.resource_manager import tags
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.resource_manager import endpoint_utils as endpoints
from googlecloudsdk.command_lib.resource_manager import tag_arguments as arguments
from googlecloudsdk.command_lib.resource_manager import tag_utils

EFFECTIVE_TAG_BINDING_COLLECTION = "effectiveTagBindingCollections/"
TAG_BINDING_COLLECTION = "tagBindingCollections/"


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class List(base.ListCommand):
  """Lists TagBindings bound to the specified resource.

    When specifying a parent resource, the full name of the parent resource must
    be used. See:
    https://cloud.google.com/apis/design/resource_names#full_resource_name.
  """

  detailed_help = {
      "EXAMPLES":
          """
          To list TagBindings for '//cloudresourcemanager.googleapis.com/projects/123' run:

            $ {command} --parent=//cloudresourcemanager.googleapis.com/projects/123
          """
  }

  @staticmethod
  def Args(parser):
    arguments.AddParentArgToParser(
        parser, message="Full resource name attached to the binding")
    arguments.AddLocationArgToParser(
        parser, ("Region or zone of the resource for listing TagBindings. This "
                 "field should not be set if the resource is a global resource "
                 "like projects, folders and organizations."))
    arguments.AddEffectiveArgToParser(
        parser,
        ("Show all effective TagBindings on the resource. TagBindings applied "
         "at a higher level will be inherited to all descendants."))

  def Run(self, args):
    show_effective = args.IsSpecified("effective")
    if self.ReleaseTrack() == base.ReleaseTrack.ALPHA:
      freeform_enabled = True
      location = args.location if args.IsSpecified("location") else "global"
      if(show_effective):
        collection_resource_name = (
            f"locations/{location}/{EFFECTIVE_TAG_BINDING_COLLECTION}{args.parent}"
        )
      else:
        collection_resource_name = (
            f"locations/{location}/{TAG_BINDING_COLLECTION}{args.parent}"
        )
      resource_name = tag_utils.GetCanonicalResourceName(
          collection_resource_name, location, base.ReleaseTrack.ALPHA)
    else:
      freeform_enabled = False
      location = args.location if args.IsSpecified("location") else None
      resource_name = tag_utils.GetCanonicalResourceName(args.parent, location,
                                                         base.ReleaseTrack.GA)

    with endpoints.CrmEndpointOverrides(location):
      messages = tags.TagMessages()

      if freeform_enabled:
        if show_effective:
          service = tags.EffectiveTagsCollectionService()
          location, _, tag_binding_collection_name = resource_name.partition(
              EFFECTIVE_TAG_BINDING_COLLECTION
          )
          encoded_resource_name = (
              f"{location}{EFFECTIVE_TAG_BINDING_COLLECTION}{urllib.parse.quote(tag_binding_collection_name, safe='')}"
          )
          list_effective_req = (
              messages.CloudresourcemanagerLocationsEffectiveTagBindingCollectionsGetRequest(
                  name=encoded_resource_name
              )
          )
          return service.Get(list_effective_req)
        else:
          service = tags.TagBindingsCollectionService()
          location, _, tag_binding_collection_name = resource_name.partition(
              TAG_BINDING_COLLECTION
          )
          encoded_resource_name = (
              f"{location}{TAG_BINDING_COLLECTION}{urllib.parse.quote(tag_binding_collection_name, safe='')}"
          )
          list_req = messages.CloudresourcemanagerLocationsTagBindingCollectionsGetRequest(
              name=encoded_resource_name
          )
          return service.Get(list_req)
      else:
        if show_effective:
          service = tags.EffectiveTagsService()
          list_effective_req = (
              messages.CloudresourcemanagerEffectiveTagsListRequest(
                  parent=resource_name
              )
          )
          return list_pager.YieldFromList(
              service,
              list_effective_req,
              batch_size_attribute="pageSize",
              batch_size=0,
              field="effectiveTags",
          )
        else:
          service = tags.TagBindingsService()
          list_req = messages.CloudresourcemanagerTagBindingsListRequest(
              parent=resource_name
          )
          return list_pager.YieldFromList(
              service,
              list_req,
              batch_size_attribute="pageSize",
              batch_size=args.page_size,
              field="tagBindings",
          )
