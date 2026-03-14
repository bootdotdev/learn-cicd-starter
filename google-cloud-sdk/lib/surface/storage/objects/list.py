# -*- coding: utf-8 -*- #
# Copyright 2022 Google LLC. All Rights Reserved.
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
"""Implementation of objects list command for getting info on objects."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.storage import cloud_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import encryption_util
from googlecloudsdk.command_lib.storage import errors
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.command_lib.storage import storage_url
from googlecloudsdk.command_lib.storage import wildcard_iterator
from googlecloudsdk.command_lib.storage.resources import contexts_only_formatter
from googlecloudsdk.command_lib.storage.resources import full_resource_formatter
from googlecloudsdk.command_lib.storage.resources import gsutil_full_resource_formatter
from googlecloudsdk.command_lib.storage.resources import resource_reference
from googlecloudsdk.command_lib.storage.resources import resource_util
from googlecloudsdk.core import log
from googlecloudsdk.core.resource import resource_printer

_COMMAND_DESCRIPTION = """
List Cloud Storage objects.

Bucket URLs like `gs://bucket` match all the objects inside a bucket,
but `gs://b*` fails because it matches a list of buckets.
"""
_GA_EXAMPLES = """
List all objects in bucket ``my-bucket'' within current directory level:

  $ {command} gs://my-bucket

List all objects across nested directories using wildcards (https://cloud.google.com/storage/docs/wildcards):

  $ {command} gs://my-bucket/**

List all objects in bucket beginning with ``o'':

  $ {command} gs://my-bucket/o*

List all objects in bucket with JSON formatting, only returning the
value of the ``name'' metadata field:

  $ {command} gs://my-bucket --format="json(name)"
"""
_ALPHA_EXAMPLES = """
List only contexts attached to objects as key value pairs.

  $ {command} gs://my-bucket --format=contextsonly
"""


def _object_iterator(
    url,
    fetch_encrypted_object_hashes,
    halt_on_empty_response,
    next_page_token,
    object_state,
    list_filter,
):
  """Iterates through resources matching URL and filter out non-objects."""
  for resource in wildcard_iterator.CloudWildcardIterator(
      url,
      error_on_missing_key=False,
      fetch_encrypted_object_hashes=fetch_encrypted_object_hashes,
      fields_scope=cloud_api.FieldsScope.FULL,
      halt_on_empty_response=halt_on_empty_response,
      next_page_token=next_page_token,
      object_state=object_state,
      list_filter=list_filter,
  ):
    if isinstance(resource, resource_reference.ObjectResource):
      yield resource


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class List(base.ListCommand):
  """Lists Cloud Storage objects."""

  detailed_help = {
      'DESCRIPTION': _COMMAND_DESCRIPTION,
      'EXAMPLES': _GA_EXAMPLES,
  }

  @classmethod
  def Args(cls, parser):
    parser.add_argument(
        'urls', nargs='+', help='Specifies URL of objects to list.')
    parser.add_argument(
        '--stat',
        action='store_true',
        help='Emulates gsutil stat-style behavior. Does not show past object'
        ' versions and changes output format.')
    flags.add_additional_headers_flag(parser)
    flags.add_encryption_flags(parser, command_only_reads_data=True)
    flags.add_fetch_encrypted_object_hashes_flag(parser, is_list=True)
    flags.add_raw_display_flag(parser)
    flags.add_soft_delete_flags(parser)
    flags.add_uri_support_to_list_commands(parser)

    if cls.ReleaseTrack() == base.ReleaseTrack.ALPHA:
      flags.add_metadata_filter_flag(parser)
      contexts_only_formatter.ContextsOnlyPrinter.Register()

  def Display(self, args, resources):
    if args.stat:
      resource_printer.Print(resources, 'object[terminator=""]')
    else:
      resource_printer.Print(resources, 'yaml')

  def Run(self, args):
    encryption_util.initialize_key_store(args)
    metadata_filter = getattr(args, 'metadata_filter', None)

    urls = []
    for url_string in args.urls:
      url = storage_url.storage_url_from_string(url_string)
      if url.is_provider() or (url.is_bucket() and
                               wildcard_iterator.contains_wildcard(
                                   url.bucket_name)):
        raise errors.InvalidUrlError(
            'URL does not match objects: {}'.format(url_string))
      if (
          metadata_filter is not None
          and url.scheme != storage_url.ProviderPrefix.GCS
      ):
        raise errors.InvalidUrlError(
            'Metadata filter is only supported for GCS URLs.'
        )
      if url.is_bucket():
        # Convert gs://bucket to gs://bucket/* to retrieve objects.
        urls.append(url.join('*'))
      else:
        urls.append(url)

    if not (args.stat or args.soft_deleted):
      object_state = cloud_api.ObjectState.LIVE_AND_NONCURRENT
    else:
      object_state = flags.get_object_state_from_flags(args)
    stat_formatter = (
        gsutil_full_resource_formatter.GsutilFullResourceFormatter()
    )
    for url in urls:
      object_iterator = _object_iterator(
          url,
          fetch_encrypted_object_hashes=args.fetch_encrypted_object_hashes,
          halt_on_empty_response=not getattr(args, 'exhaustive', False),
          next_page_token=getattr(args, 'next_page_token', None),
          object_state=object_state,
          list_filter=metadata_filter,
      )
      if args.stat:
        # Replicating gsutil "stat" command behavior.
        found_match = False
        for resource in object_iterator:
          found_match = True
          yield stat_formatter.format_object(resource, show_acl=False)
        if not found_match:
          log.error('No URLs matched: ' + url.url_string)
          self.exit_code = 1
      else:
        for resource in object_iterator:
          if args.format == contexts_only_formatter.CONTEXT_ONLY_PRINTER_FORMAT:
            yield resource
          else:
            yield resource_util.get_display_dict_for_resource(
                resource,
                full_resource_formatter.ObjectDisplayTitlesAndDefaults,
                display_raw_keys=args.raw,
            )


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ListAlpha(List):
  """Lists Cloud Storage objects."""

  detailed_help = {
      'DESCRIPTION': _COMMAND_DESCRIPTION,
      'EXAMPLES': _GA_EXAMPLES + _ALPHA_EXAMPLES,
  }
