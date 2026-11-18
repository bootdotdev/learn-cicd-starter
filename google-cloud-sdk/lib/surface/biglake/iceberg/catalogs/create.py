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
"""The create command for BigLake Iceberg REST catalogs."""

import textwrap

from googlecloudsdk.api_lib.biglake import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.biglake import flags
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class CreateCatalog(base.CreateCommand):
  """Create a BigLake Iceberg REST catalog."""

  detailed_help = {
      'EXAMPLES':
          textwrap.dedent("""\
          To add a catalog using a GCS bucket `my-catalog-bucket`, run:

            $ {command} my-catalog-bucket --catalog-type=gcs-bucket

          To create a catalog using a GCS bucket `my-catalog-bucket` with vended credentials, run:

            $ {command} my-catalog-bucket --catalog-type=gcs-bucket   --credential-mode=vended-credentials

          """),
  }

  @staticmethod
  def Args(parser):
    flags.AddCatalogResourceArg(parser, 'to create')
    util.GetCredentialModeEnumMapper(
        base.ReleaseTrack.ALPHA
    ).choice_arg.AddToParser(parser)
    util.GetCatalogTypeEnumMapper(
        base.ReleaseTrack.ALPHA
    ).choice_arg.AddToParser(parser)

  def Run(self, args):
    client = util.GetClientInstance(self.ReleaseTrack())
    messages = client.MESSAGES_MODULE

    catalog_name = util.GetCatalogName(args.catalog)

    credential_mode = None
    if args.IsSpecified('credential_mode'):
      credential_mode = util.GetCredentialModeEnumMapper(
          self.ReleaseTrack()
      ).GetEnumForChoice(args.credential_mode)

    catalog = messages.IcebergCatalog(
        name=catalog_name,
        catalog_type=util.GetCatalogTypeEnumMapper(
            self.ReleaseTrack()
        ).GetEnumForChoice(args.catalog_type),
        credential_mode=credential_mode,
    )

    request = (
        messages.BiglakeIcebergV1RestcatalogExtensionsProjectsCatalogsCreateRequest(
            iceberg_catalog_id=args.catalog,
            icebergCatalog=catalog,
            parent=util.GetParentName(),
        )
    )
    log.CreatedResource(catalog_name, 'catalog')
    return client.iceberg_v1_restcatalog_extensions_projects_catalogs.Create(
        request
    )
