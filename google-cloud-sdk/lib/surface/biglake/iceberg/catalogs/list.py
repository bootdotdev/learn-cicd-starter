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
"""The list command for BigLake Iceberg REST catalogs."""

from googlecloudsdk.api_lib.biglake import util
from googlecloudsdk.calliope import base


def _GetUriFunction(resource):
  return util.GetCatalogRef(resource.name).SelfLink()


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class ListIcebergCatalogs(base.ListCommand):
  """List BigLake Iceberg REST catalogs."""

  @staticmethod
  def Args(parser):
    parser.display_info.AddFormat("""
          table(
            name:sort=1,
            name.basename():label=CATALOG-ID,
            catalog-type,
            storage-regions,
            replicas
          )
        """)
    parser.display_info.AddUriFunc(_GetUriFunction)

  def Run(self, args):
    client = util.GetClientInstance(self.ReleaseTrack())
    messages = client.MESSAGES_MODULE

    parent_name = util.GetParentName()
    request = messages.BiglakeIcebergV1RestcatalogExtensionsProjectsCatalogsListRequest(
        parent=parent_name
    )

    response = client.iceberg_v1_restcatalog_extensions_projects_catalogs.List(
        request
    )
    return response.iceberg_catalogs
