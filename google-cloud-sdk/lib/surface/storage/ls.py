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

"""Command to list Cloud Storage resources."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.storage import cloud_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import encryption_util
from googlecloudsdk.command_lib.storage import errors
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.command_lib.storage import list_util
from googlecloudsdk.command_lib.storage import ls_command_util
from googlecloudsdk.command_lib.storage import stdin_iterator
from googlecloudsdk.command_lib.storage import storage_url
from googlecloudsdk.core import log


_COMMAND_DESCRIPTION = """
List your Cloud Storage buckets in a project and objects in a bucket.
This command treats forward slashes in object names as directories. See
below for examples of how to use wildcards to get the listing behavior
you want.
"""
_GA_EXAMPLES = """
The following command lists the buckets in the default project:

  $ {command}

The following command lists the buckets in the specified project:

  $ {command} --project=my-project

The following command lists the contents of a bucket:

  $ {command} gs://my-bucket

You can use [wildcards](https://cloud.google.com/storage/docs/wildcards)
to match multiple paths (including multiple buckets). Bucket wildcards are
expanded to match only buckets contained in your current project. The
following command matches ``.txt'' objects that begin with ``log'' and
that are stored in buckets in your project that begin with ``my-b'':

  $ {command} gs://my-b*/log*.txt

You can use double-star wildcards to match zero or more directory levels
in a path. The following command matches all ``.txt'' objects in a bucket.

  $ {command} gs://my-bucket/**/*.txt

The wildcard `**` retrieves a flat list of objects in a single API call
and does not match prefixes. The following command would not match
`gs://my-bucket/dir/log.txt`:

  $ {command} gs://my-bucket/**/dir

Double-star expansion also can not be combined with other expressions in a
given path segment and operates as a single star in that context. For
example, the command `gs://my-bucket/dir**/log.txt` is treated as
`gs://my-bucket/dir*/log.txt`. To get the recursive behavior, the command
should instead be written the following way:

  gs://my-bucket/dir*/**/log.txt

The following command lists all items recursively with formatting by
using `--recursive`:

  $ {command} --recursive gs://bucket

Recursive listings are similar to `**` except recursive listings include
line breaks and header formatting for each subdirectory.
"""
_ALPHA_EXAMPLES = """
The following command filters objects based on specified filter while listing.
Note that the flag is only supported for Google Cloud Storage URLs and only
applies to objects. This means that directories or buckets will still be listed
even if they do not contain objects that match the filter.

  $ {command} gs://my-bucket --metadata-filter='contexts."foo"="bar"'

"""


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Ls(base.Command):
  """List Cloud Storage buckets and objects."""

  # pylint:disable=g-backslash-continuation
  detailed_help = {
      'DESCRIPTION': _COMMAND_DESCRIPTION,
      'EXAMPLES': _GA_EXAMPLES,
  }
  # pylint:enable=g-backslash-continuation

  @classmethod
  def Args(cls, parser):
    """Edit argparse.ArgumentParser for the command."""
    parser.add_argument(
        'path',
        nargs='*',
        help=(
            'The path of objects and directories to list. The path must begin'
            ' with gs:// and is allowed to contain wildcard characters.'
        ),
    )
    parser.add_argument(
        '-a',
        '--all-versions',
        action='store_true',
        help=(
            'Include noncurrent object versions in the listing. This flag is'
            ' typically only useful for buckets with [object'
            ' versioning](https://cloud.google.com/storage/docs/object-versioning)'
            ' enabled. If combined with the `--long` option, the metageneration'
            ' for each listed object is also included.'
        ),
    )
    parser.add_argument(
        '-b',
        '--buckets',
        action='store_true',
        help=(
            'When given a bucket URL, only return buckets. Useful for avoiding'
            ' the rule that prints the top-level objects of buckets matching a'
            ' query. Typically used in combination with `--full` to get the'
            ' full metadata of buckets.'
        ),
    )
    parser.add_argument(
        '-e',
        '--etag',
        action='store_true',
        help='Include ETag metadata in listings that use the `--long` flag.',
    )
    parser.add_argument(
        '--format',
        help=(
            'Use "gsutil" to get the style of the older gsutil CLI. (e.g.'
            ' "--format=gsutil"). Other format values (e.g. "json") do not'
            ' work. See different ls flags and commands for alternative'
            ' formatting.'
        ),
    )
    parser.add_argument(
        '--readable-sizes',
        action='store_true',
        help=(
            'When used with `--long`, print object sizes in human'
            ' readable format, such as 1 KiB, 234 MiB, or 2 GiB.'
        ),
    )
    parser.add_argument(
        '-R',
        '-r',
        '--recursive',
        action='store_true',
        help=(
            'Recursively list the contents of any directories that match the'
            ' path expression.'
        ),
    )

    output_styles = parser.add_group(mutex='True')
    output_styles.add_argument(
        '-l',
        '--long',
        action='store_true',
        help='For objects only. List size in bytes, creation time, and URL.',
    )
    output_styles.add_argument(
        '-L',
        '--full',
        action='store_true',
        help='List all available metadata about items in rows.',
    )
    output_styles.add_argument(
        '-j',
        '--json',
        action='store_true',
        help='List all available metadata about items as a JSON dump.',
    )

    flags.add_additional_headers_flag(parser)
    flags.add_encryption_flags(parser, command_only_reads_data=True)
    flags.add_fetch_encrypted_object_hashes_flag(parser, is_list=True)
    flags.add_read_paths_from_stdin_flag(parser)
    flags.add_soft_delete_flags(parser)

    if cls.ReleaseTrack() == base.ReleaseTrack.ALPHA:
      flags.add_metadata_filter_flag(parser)

  @classmethod
  def _get_args(cls, args):
    """Get the args for the command."""
    soft_deleted = getattr(args, 'soft_deleted', False)
    all_versions = getattr(args, 'all_versions', False)
    buckets = getattr(args, 'buckets', False)
    return soft_deleted, all_versions, buckets

  def Run(self, args):
    """Command execution logic."""

    encryption_util.initialize_key_store(args)

    # We cannot do a backward incompatible change, and thus we are throwing a
    # warning here so that users in the long term can avoid using the flags
    # incorrectly.
    soft_deleted, all_versions, buckets = self._get_args(args)
    # We do not support operations for soft deleted resources combined with
    # --all-versions flag.
    if soft_deleted and all_versions:
      log.warning(
          'The --all-versions flag has no effect when used with the'
          ' --soft-deleted flag. When --soft-deleted is used, all'
          ' soft-deleted versions of the resource are returned.'
      )
    # When listing buckets, only --soft-deleted flag is allowed.
    if buckets and all_versions:
      log.warning('The --all-versions flag has no effect when listing buckets.')

    use_gsutil_style = flags.check_if_use_gsutil_style(args)

    found_non_default_provider = False
    if args.path or args.read_paths_from_stdin:
      paths = stdin_iterator.get_urls_iterable(
          args.path, args.read_paths_from_stdin, allow_empty=True
      )
    else:
      paths = [cloud_api.DEFAULT_PROVIDER.value + '://']

    metadata_filter = getattr(args, 'metadata_filter', None)
    storage_urls = [storage_url.storage_url_from_string(path) for path in paths]
    for url in storage_urls:
      if not isinstance(url, storage_url.CloudUrl):
        raise errors.InvalidUrlError(
            'Ls only works for cloud URLs. Error for: {}'.format(url.url_string)
        )
      if (
          metadata_filter is not None
          and url.scheme != cloud_api.DEFAULT_PROVIDER
      ):
        raise errors.Error('Metadata filter is only supported for GCS URLs.')
      if url.scheme is not cloud_api.DEFAULT_PROVIDER:
        found_non_default_provider = True

    if args.full:
      display_detail = list_util.DisplayDetail.FULL
    elif args.json:
      display_detail = list_util.DisplayDetail.JSON
    elif args.long:
      display_detail = list_util.DisplayDetail.LONG
    else:
      display_detail = list_util.DisplayDetail.SHORT

    ls_command_util.LsExecutor(
        storage_urls,
        buckets_flag=buckets,
        display_detail=display_detail,
        fetch_encrypted_object_hashes=args.fetch_encrypted_object_hashes,
        halt_on_empty_response=not getattr(args, 'exhaustive', False),
        include_etag=args.etag,
        include_managed_folders=True,
        next_page_token=getattr(args, 'next_page_token', None),
        object_state=flags.get_object_state_from_flags(args),
        readable_sizes=args.readable_sizes,
        recursion_flag=args.recursive,
        use_gsutil_style=use_gsutil_style,
        soft_deleted_buckets=buckets and soft_deleted,
        list_filter=metadata_filter,
    ).list_urls()

    if found_non_default_provider and args.full:
      # We do guarantee full-style formatting for all metadata fields of
      # non-GCS providers. In this case, data is hidden.
      log.warning('For additional metadata information, please run ls --json.')


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class LsAlpha(Ls):
  """List Cloud Storage buckets and objects."""

  detailed_help = {
      'DESCRIPTION': _COMMAND_DESCRIPTION,
      'EXAMPLES': _GA_EXAMPLES + _ALPHA_EXAMPLES,
  }
