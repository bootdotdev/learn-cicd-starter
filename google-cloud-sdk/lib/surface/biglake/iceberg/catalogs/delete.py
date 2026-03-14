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
"""The delete command for BigLake Iceberg REST catalogs."""

from googlecloudsdk.api_lib.biglake import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.biglake import flags
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class DeleteCatalog(base.DeleteCommand):
  """Delete a BigLake Iceberg REST catalog."""

  @staticmethod
  def Args(parser):
    flags.AddCatalogResourceArg(parser, 'to delete')

  def Run(self, args):
    client = util.GetClientInstance(self.ReleaseTrack())
    messages = util.GetMessagesModule(self.ReleaseTrack())

    catalog_name = util.GetCatalogName(args.catalog)

    request = messages.BiglakeIcebergV1RestcatalogExtensionsProjectsCatalogsDeleteRequest(
        name=catalog_name
    )

    response = (
        client.iceberg_v1_restcatalog_extensions_projects_catalogs.Delete(
            request
        )
    )
    log.DeletedResource(catalog_name, 'catalog')
    return response
