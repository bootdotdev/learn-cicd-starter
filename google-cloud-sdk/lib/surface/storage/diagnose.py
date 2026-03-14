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

"""Diagnose Google Cloud Storage common issues."""

import enum
import os

from googlecloudsdk.api_lib.storage import errors as api_errors
from googlecloudsdk.api_lib.storage.gcs_json import client as gcs_json_client
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.storage import errors as command_errors
from googlecloudsdk.command_lib.storage import errors_util
from googlecloudsdk.command_lib.storage import storage_url
from googlecloudsdk.command_lib.storage.diagnose import direct_connectivity_diagnostic
from googlecloudsdk.command_lib.storage.diagnose import download_throughput_diagnostic as download_throughput_diagnostic_lib
from googlecloudsdk.command_lib.storage.diagnose import export_util
from googlecloudsdk.command_lib.storage.diagnose import latency_diagnostic as latency_diagnostic_lib
from googlecloudsdk.command_lib.storage.diagnose import system_info
from googlecloudsdk.command_lib.storage.diagnose import upload_throughput_diagnostic as upload_throughput_diagnostic_lib
from googlecloudsdk.command_lib.storage.resources import gcs_resource_reference
from googlecloudsdk.core import log

_OBJECT_SIZE_UPPER_BOUND = '1GB'


def get_bucket_resource(
    bucket_url: storage_url.StorageUrl,
) -> gcs_resource_reference.GcsBucketResource:
  """Fetches the bucket resource for the given bucket storage URL.

  Args:
    bucket_url: The URL object to get the bucket resource for.

  Returns:
    The bucket resource for the given URL.

  Raises:
    FatalError: If the bucket resource could not be fetched.
  """
  gcs_client = gcs_json_client.JsonClient()
  try:
    return gcs_client.get_bucket(bucket_url.bucket_name)
  except api_errors.CloudApiError as e:
    raise command_errors.FatalError(
        f'Bucket metadata could not be fetched for {bucket_url.bucket_name}'
    ) from e


def _validate_args(args):
  """Validates and raises error if the command arguments are invalid."""
  errors_util.raise_error_if_not_gcs_bucket(
      args.command_path, storage_url.storage_url_from_string(args.url)
  )

  if (
      args.export
      and args.destination
      and not (
          os.path.exists(args.destination) and os.path.isdir(args.destination)
      )
  ):
    raise ValueError(
        f'Invalid destination path: {args.destination}. Please provide'
        ' a valid path.'
    )


class TestType(enum.Enum):
  """Enum class for specifying performance test type for diagnostic tests."""

  DIRECT_CONNECTIVITY = 'DIRECT_CONNECTIVITY'
  DOWNLOAD_THROUGHPUT = 'DOWNLOAD_THROUGHPUT'
  UPLOAD_THROUGHPUT = 'UPLOAD_THROUGHPUT'
  LATENCY = 'LATENCY'


@base.DefaultUniverseOnly
class Diagnose(base.Command):
  """Diagnose Google Cloud Storage."""

  detailed_help = {
      'DESCRIPTION': """
      The diagnose command runs a series of diagnostic tests for common gcloud
      storage issues.

      The `URL` argument must name an exisiting bucket for which the user
      already has write permissions. Standard billing also applies.
      Several test files/objects will be uploaded and downloaded to this bucket
      to gauge out the performance metrics. All the temporary files will be
      deleted on successfull completion of the command.

      By default, the command executes `DOWNLOAD_THROUGHPUT`,
      `UPLOAD_THROUGHPUT` and `LATENCY` tests. Tests to execute can be overriden
      by using the `--test-type` flag.
      Each test uses the command defaults or gcloud CLI configurations for
      performing the operations. This command also provides a way to override
      these values via means of different flags like `--process-count`,
      `--thread-count`, `--download-type`, etc.

      The command outputs a diagnostic report with sytem information like free
      memory, available CPU, average CPU load per test, disk counter deltas and
      diagnostic information specific to individual tests on successful
      completion.

      """,
      'EXAMPLES': """

      The following command runs the default diagnostic tests on ``my-bucket''
      bucket:

      $ {command} gs://my-bucket

      The following command runs only UPLOAD_THROUGHPUT and DOWNLOAD_THROUGHPUT
      diagnostic tests:

      $ {command} gs://my-bucket --test-type=UPLOAD_THROUGHPUT,DOWNLOAD_THROUGHPUT

      The following command runs the diagnostic tests using ``10'' objects of
      ``1MiB'' size each with ``10'' threads and ``10'' processes at max:

      $ {command} gs://my-bucket --no-of-objects=10 --object-size=1MiB
      --process-count=10 --thread-count=10

      The following command can be used to bundle and export the diagnostic
      information to a user defined ``PATH'' destination:

      $ {command} gs://my-bucket --export --destination=<PATH>
      """,
  }

  @classmethod
  def Args(cls, parser):
    parser.SetSortArgs(False)

    parser.add_argument(
        'url',
        type=str,
        help='Bucket URL to use for the diagnostic tests.',
    )
    parser.add_argument(
        '--test-type',
        type=arg_parsers.ArgList(
            choices=sorted([option.value for option in TestType])
        ),
        metavar='TEST_TYPES',
        help="""
        Tests to run as part of this diagnosis. Following tests are supported:

        DIRECT_CONNECTIVITY: Run a test upload over the Direct Connectivity
        network path and run other diagnostics if the upload fails.

        DOWNLOAD_THROUGHPUT: Upload objects to the specified bucket and record
        the number of bytes transferred per second.

        UPLOAD_THROUGHPUT: Download objects from the specified bucket and
        record the number of bytes transferred per second.

        LATENCY: Write the objects, retrieve their metadata, read the objects,
        and record latency of each operation.
        """,
        default=[],
    )
    parser.add_argument(
        '--download-type',
        choices=sorted([
            option.value
            for option in download_throughput_diagnostic_lib.DownloadType
        ]),
        default=download_throughput_diagnostic_lib.DownloadType.FILE,
        help="""
        Download strategy to use for the DOWNLOAD_THROUGHPUT diagnostic test.

        STREAMING: Downloads the file in memory, does not use parallelism.
        `--process-count` and `--thread-count` flag values will be ignored if
        provided.

        SLICED: Performs a [sliced download](https://cloud.google.com/storage/docs/sliced-object-downloads)
        of objects to a directory.
        Parallelism can be controlled via `--process-count` and `--thread-count`
        flags.

        FILE: Download objects as files. Parallelism can be controlled via
        `--process-count` and `--thread-count` flags.
        """,
    )
    parser.add_argument(
        '--logs-path',
        help=(
            'If the diagnostic supports writing logs, write the logs to this'
            ' file location.'
        ),
    )
    parser.add_argument(
        '--upload-type',
        choices=sorted([
            option.value
            for option in upload_throughput_diagnostic_lib.UploadType
        ]),
        default=upload_throughput_diagnostic_lib.UploadType.FILE,
        help="""
        Upload strategy to use for the _UPLOAD_THROUGHPUT_ diagnostic test.

        FILE: Uploads files to a bucket. Parallelism can be controlled via
        `--process-count` and `--thread-count` flags.

        PARALLEL_COMPOSITE: Uploads files using a [parallel
        composite strategy](https://cloud.google.com/storage/docs/parallel-composite-uploads).
        Parallelism can be controlled via `--process-count` and `--thread-count`
        flags.

        STREAMING: Streams the data to the bucket, does not use parallelism.
        `--process-count` and `--thread-count` flag values will be ignored if
        provided.
        """,
    )

    parser.add_argument(
        '--process-count',
        type=arg_parsers.BoundedInt(lower_bound=1),
        help='Number of processes at max to use for each diagnostic test.',
    )
    parser.add_argument(
        '--thread-count',
        type=arg_parsers.BoundedInt(lower_bound=1),
        help='Number of threads at max to use for each diagnostic test.',
    )

    object_properties_group = parser.add_group(
        sort_args=False, help='Object properties:'
    )

    object_properties_group.add_argument(
        '--object-count',
        required=True,
        type=arg_parsers.BoundedInt(lower_bound=1),
        help='Number of objects to use for each diagnostic test.',
    )

    object_size_properties_group = object_properties_group.add_group(
        mutex=True,
        sort_args=False,
        help='Object size properties:',
        required=True,
    )
    object_size_properties_group.add_argument(
        '--object-size',
        type=arg_parsers.BinarySize(upper_bound=_OBJECT_SIZE_UPPER_BOUND),
        help='Object size to use for the diagnostic tests.',
    )
    object_size_properties_group.add_argument(
        '--object-sizes',
        metavar='OBJECT_SIZES',
        type=arg_parsers.ArgList(
            element_type=arg_parsers.BinarySize(
                upper_bound=_OBJECT_SIZE_UPPER_BOUND
            )
        ),
        help="""
        List of object sizes to use for the tests. Sizes should be
        provided for each object specified using `--object-count` flag.
        """,
    )

    export_group = parser.add_group(
        sort_args=False, help='Export diagnostic bundle.'
    )
    export_group.add_argument(
        '--export',
        action='store_true',
        required=True,
        help="""
        Generate and export a diagnostic bundle. The following
        information will be bundled and exported into a gzipped tarball
        (.tar.gz):

        - Latest gcloud CLI logs.
        - Output of running the `gcloud storage diagnose` command.
        - Output of running the `gcloud info --anonymize` command.

        Note: This command generates a bundle containing system information like
        disk counter detlas, CPU information and system configurations. Please
        exercise caution while sharing.
        """,
    )
    export_group.add_argument(
        '--destination',
        type=str,
        help=(
            'Destination file path where the diagnostic bundle will be'
            ' exported.'
        ),
    )
    parser.display_info.AddFormat("""
                                  table(
                                    name,
                                    operation_results[]:format='table[box](name,payload_description:wrap,result:wrap)'
                                  )
                                  """)

  def _run_tests_with_performance_tracking(
      self, args, url_object, tests_to_run
  ):
    """Runs test with system performance tracking."""
    object_sizes = None

    if args.object_count:
      if args.object_sizes:
        if len(args.object_sizes) != args.object_count:
          raise ValueError(
              'Number of object sizes provided should match the number of'
              ' objects.'
          )
        else:
          object_sizes = args.object_sizes
      elif args.object_size:
        object_sizes = [args.object_size] * args.object_count

    system_info_provider = system_info.get_system_info_provider()
    test_results = []
    with system_info.get_disk_io_stats_delta_diagnostic_result(
        system_info_provider, test_results
    ):
      if TestType.LATENCY.value in tests_to_run:
        latency_diagnostic = latency_diagnostic_lib.LatencyDiagnostic(
            url_object,
            object_sizes,
        )
        latency_diagnostic.execute()
        test_results.append(latency_diagnostic.result)

      if TestType.DOWNLOAD_THROUGHPUT.value in tests_to_run:
        download_type = download_throughput_diagnostic_lib.DownloadType(
            args.download_type
        )
        download_throughput_diagnostic = (
            download_throughput_diagnostic_lib.DownloadThroughputDiagnostic(
                url_object,
                download_type,
                object_sizes,
                process_count=args.process_count,
                thread_count=args.thread_count,
            )
        )
        download_throughput_diagnostic.execute()
        test_results.append(download_throughput_diagnostic.result)

      if TestType.UPLOAD_THROUGHPUT.value in tests_to_run:
        upload_type = upload_throughput_diagnostic_lib.UploadType(
            args.upload_type
        )
        upload_throughput_diagnostic = (
            upload_throughput_diagnostic_lib.UploadThroughputDiagnostic(
                url_object,
                upload_type,
                object_sizes,
                process_count=args.process_count,
                thread_count=args.thread_count,
            )
        )
        upload_throughput_diagnostic.execute()
        test_results.append(upload_throughput_diagnostic.result)

      # Capture the system information at last to CPU load avg could account for
      # the diagnostic test runs.
      test_results.append(
          system_info.get_system_info_diagnostic_result(system_info_provider)
      )
      return test_results

  def Run(self, args):

    default_tests = [
        TestType.DOWNLOAD_THROUGHPUT.value,
        TestType.LATENCY.value,
        TestType.UPLOAD_THROUGHPUT.value,
    ]

    _validate_args(args)
    url_object = storage_url.storage_url_from_string(args.url)
    bucket_resource = get_bucket_resource(url_object)

    log.status.Print(
        f'Using {bucket_resource.name} bucket for the diagnostic tests.'
    )
    log.status.Print(f'Bucket location : {bucket_resource.location}')
    log.status.Print(
        f'Bucket storage class : {bucket_resource.default_storage_class}'
    )

    if args.test_type:
      tests_to_run = args.test_type
    else:
      tests_to_run = default_tests

    if tests_to_run == [TestType.DIRECT_CONNECTIVITY.value]:
      test_results = []
    else:
      test_results = self._run_tests_with_performance_tracking(
          args, url_object, tests_to_run
      )

    if TestType.DIRECT_CONNECTIVITY.value in tests_to_run:
      direct_connectivity = (
          direct_connectivity_diagnostic.DirectConnectivityDiagnostic(
              bucket_resource,
              logs_path=args.logs_path,
          )
      )
      direct_connectivity.execute()
      test_results.append(direct_connectivity.result)

    if args.export:
      log.status.Print('Exporting diagnostic bundle...')
      export_path = export_util.export_diagnostic_bundle(
          test_results, args.destination
      )
      log.status.Print(
          'Successfully exported diagnostic bundle to {}'.format(export_path)
      )
      return None

    log.status.Print('Generating diagnostic report...')
    return test_results
