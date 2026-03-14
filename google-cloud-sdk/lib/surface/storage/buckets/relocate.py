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

"""Implementation of buckets relocate command."""

import textwrap

from googlecloudsdk.api_lib.storage import api_factory
from googlecloudsdk.api_lib.storage import errors as api_errors
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import errors as command_errors
from googlecloudsdk.command_lib.storage import errors_util
from googlecloudsdk.command_lib.storage import flags
from googlecloudsdk.command_lib.storage import operations_util
from googlecloudsdk.command_lib.storage import storage_url
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


_BUCKET_RELCOCATION_WRITE_DOWNTIME_WARNING = textwrap.dedent("""
1. This move will involve write downtime.
2. In-flight resumable uploads not finished before the write downtime will be \
lost.
3. Bucket tags added to the bucket will result in the relocation being canceled.
4. Please ensure that you have sufficient quota in the destination before \
performing the relocation.
""")

_BUCKET_RELOCATION_WITHOUT_WRITE_DOWNTIME_WARNING = textwrap.dedent("""
1. This is a policy change move (no write downtime).
2. Please ensure that you have sufficient quota in the destination before \
performing the relocation.
""")

_ADVANCING_BUCKET_RELOCATION_WARNING = textwrap.dedent("""
1. Any ongoing, in-flight resumable uploads will be canceled and lost.
2. Write downtime will be incurred.
""")


def _get_bucket_resource(gcs_client, bucket_url):
  """Fetches the bucket resource for the given bucket storage URL."""
  try:
    return gcs_client.get_bucket(bucket_url.bucket_name)
  except api_errors.CloudApiError as e:
    raise command_errors.FatalError(e) from e


def _prompt_user_to_confirm_the_relocation(bucket_resource, args):
  """Prompt the user to confirm the relocation."""
  if args.dry_run:
    return

  source_location = f'{bucket_resource.location}'
  if bucket_resource.data_locations:
    source_location += f' {bucket_resource.data_locations}'

  if bucket_resource.location.casefold() == args.location.casefold():
    warning_message = _BUCKET_RELOCATION_WITHOUT_WRITE_DOWNTIME_WARNING
  else:
    warning_message = _BUCKET_RELCOCATION_WRITE_DOWNTIME_WARNING

  log.warning(f'The bucket {args.url} is in {source_location}.')
  log.warning(warning_message)

  console_io.PromptContinue(
      prompt_string=(
          "Please acknowledge that you've read the above warnings and want to"
          f' relocate the bucket {args.url}?'
      ),
      cancel_on_no=True,
  )

  log.status.Print(f'Starting bucket relocation for {args.url}...\n')


def _prompt_user_to_confirm_advancing_the_relocation(bucket_name):
  """Prompt the user to confirm advancing the relocation."""
  log.warning(_ADVANCING_BUCKET_RELOCATION_WARNING)
  console_io.PromptContinue(
      prompt_string=(
          'This will start the write downtime for your relocation of gs://'
          f'{bucket_name}, are you sure you want to continue?'
      ),
      cancel_on_no=True,
  )


# TODO: b/361729720 - Make bucket-relocate command group universe compatible.
@base.DefaultUniverseOnly
class Relocate(base.Command):
  """Relocates bucket between different locations."""

  detailed_help = {
      'DESCRIPTION': """
      Relocates a bucket between different locations.
      """,
      'EXAMPLES': """
      To move a bucket (``gs://my-bucket'') to the ``us-central1'' location, use
      the following command:

          $ {command} gs://my-bucket --location=us-central1

      To move a bucket to a custom dual-region, use the following command:

          $ {command} gs://my-bucket --location=us
              --placement=us-central1,us-east1

      To validate the operation without actually moving the bucket, use the
      following command:

          $ {command} gs://my-bucket --location=us-central1 --dry-run

      To schedule a write lock for the move, with ttl for reverting the write
      lock after 7h, if the relocation has not succeeded, use the following
      command:

          $ {command}
              --operation=projects/_/buckets/my-bucket/operations/C894F35J
              --finalize --ttl=7h
      """,
  }

  @classmethod
  def Args(cls, parser):
    parser.SetSortArgs(False)
    relocate_arguments_group = parser.add_mutually_exclusive_group(
        required=True
    )
    bucket_relocate_group = relocate_arguments_group.add_group(
        'Arguments for initiating the bucket relocate operation.'
    )
    bucket_relocate_group.SetSortArgs(False)
    bucket_relocate_group.add_argument(
        'url',
        type=str,
        help='The URL of the bucket to relocate.',
    )
    bucket_relocate_group.add_argument(
        '--location',
        type=str,
        required=True,
        help=(
            'The final [location]'
            '(https://cloud.google.com/storage/docs/locations) where the'
            ' bucket will be relocated to. If no location is provided, Cloud'
            ' Storage will use the default location, which is us.'
        ),
    )
    flags.add_placement_flag(bucket_relocate_group)
    bucket_relocate_group.add_argument(
        '--dry-run',
        action='store_true',
        help=(
            'Prints the operations that the relocate command would perform'
            ' without actually performing relocation. This is helpful to'
            ' identify any issues that need to be detected asynchronously.'
        ),
    )

    advance_relocate_operation_group = relocate_arguments_group.add_group(
        'Arguments for advancing the relocation operation.'
    )
    advance_relocate_operation_group.SetSortArgs(False)
    advance_relocate_operation_group.add_argument(
        '--operation',
        type=str,
        required=True,
        help=(
            'Specify the relocation operation name to advance the relocation'
            ' operation.The relocation operation name must include the Cloud'
            ' Storage bucket and operation ID.'
        ),
    )
    advance_relocate_operation_group.add_argument(
        '--finalize',
        action='store_true',
        required=True,
        help=(
            'Schedules the write lock to occur. Once activated, no further'
            ' writes will be allowed to the associated bucket. This helps'
            ' minimize disruption to bucket usage. For certain types of'
            ' moves(between Multi Region and Custom Dual Regions), finalize is'
            ' not required.'
        ),
    )
    advance_relocate_operation_group.add_argument(
        '--ttl',
        type=arg_parsers.Duration(),
        help=(
            'Time to live for the relocation operation. Defaults to 12h if not'
            ' provided.'
        ),
    )

  def Run(self, args):
    gcs_client = api_factory.get_api(storage_url.ProviderPrefix.GCS)

    if args.url:
      url = storage_url.storage_url_from_string(args.url)
      errors_util.raise_error_if_not_gcs_bucket(args.command_path, url)

      bucket_resource = _get_bucket_resource(gcs_client, url)
      _prompt_user_to_confirm_the_relocation(bucket_resource, args)

      return gcs_client.relocate_bucket(
          url.bucket_name,
          args.location,
          args.placement,
          args.dry_run,
      )

    bucket, operation_id = (
        operations_util.get_operation_bucket_and_id_from_name(args.operation)
    )
    _prompt_user_to_confirm_advancing_the_relocation(bucket)
    gcs_client.advance_relocate_bucket(bucket, operation_id, args.ttl)
    log.status.Print(
        f'Sent request to advance relocation for bucket gs://{bucket} with'
        f' operation {operation_id}.'
    )
