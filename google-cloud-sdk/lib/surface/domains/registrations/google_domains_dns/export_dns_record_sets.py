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
"""`gcloud domains registrations google-domains-dns export-dns-record-sets` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.dns import export_util
from googlecloudsdk.api_lib.domains import registrations
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.domains import resource_args
from googlecloudsdk.command_lib.domains import util
from googlecloudsdk.core import log
from googlecloudsdk.core.util import files


class ResourceRecordSet:

  def __init__(self, name, record_type, ttl, rrdatas):
    self.name = name
    self.type = record_type
    self.ttl = ttl
    self.rrdatas = rrdatas


@base.DefaultUniverseOnly
class ExportDNSRecordSets(base.Command):
  """Export your registration's Google Domains DNS zone's record-sets into a file.

  Export your registration's Google Domains DNS (deprecated) zone's record-sets
  into a file.
  The formats you can export to are YAML records format (default) and
  BIND zone file format.

  ## EXAMPLES

  To export DNS record-sets of ``example.com'' into a YAML file, run:

    $ gcloud domains registrations google-domains-dns export-dns-record-sets
    example.com --records-file=records.yaml

  To export DNS record-sets of ``example.com'' into a BIND zone formatted file,
  run:

    $ gcloud domains registrations google-domains-dns export-dns-record-sets
    example.com --records-file=records.zonefile --zone-file-format
  """

  @staticmethod
  def Args(parser):
    resource_args.AddRegistrationResourceArg(
        parser, 'to get the DNS records for'
    )
    parser.add_argument(
        '--records-file',
        required=True,
        help='File to which record-sets should be exported.',
    )
    parser.add_argument(
        '--zone-file-format',
        required=False,
        action='store_true',
        help=(
            'Indicates that records-file should be in the zone file format. '
            'When using this flag, expect the record-set '
            'to be exported to a BIND zone formatted file. If you omit this '
            'flag, the record-set is exported into a YAML formatted records '
            'file. Note, this format flag determines the format of the '
            'output recorded in the records-file; it is different from the '
            'global `--format` flag which affects console output alone.'
        ),
    )

  def Run(self, args):
    api_version = registrations.GetApiVersionFromArgs(args)
    client = registrations.RegistrationsClient(api_version)
    args.registration = util.NormalizeResourceName(args.registration)
    registration_ref = args.CONCEPTS.registration.Parse()

    # Get all the record-sets.
    record_sets = []
    page_token = ''
    while True:
      resp = client.RetrieveGoogleDomainsDnsRecords(
          registration_ref, page_token=page_token, page_size=0
      )
      rrset = resp.rrset
      if rrset is not None:
        for rr in rrset:
          record_sets.append(
              ResourceRecordSet(rr.name, rr.type, rr.ttl, rr.rrdata)
          )
      page_token = resp.nextPageToken
      if not page_token:
        break

    # Export the record-sets.
    try:
      with files.FileWriter(args.records_file) as export_file:
        if args.zone_file_format:
          export_util.WriteToZoneFile(
              export_file,
              record_sets,
              registration_ref.registrationsId,  # domain name
          )
        else:
          export_util.WriteToYamlFile(export_file, record_sets)
    except Exception as exp:
      msg = 'Unable to export record-sets to file [{0}]: {1}'.format(
          args.records_file, exp
      )
      raise export_util.UnableToExportRecordsToFile(msg)

    log.status.Print('Exported record-sets to [{0}].'.format(args.records_file))
