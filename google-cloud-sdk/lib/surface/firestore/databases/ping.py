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
"""The gcloud Firestore databases ping command."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import itertools
import statistics
import textwrap
import time

from googlecloudsdk.api_lib.firestore import databases
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.firestore import connection_util
from googlecloudsdk.command_lib.firestore import flags
from googlecloudsdk.core import properties


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Ping(base.Command):
  """Times the connection and ping time for a Firestore with MongoDB compatibility database.

  ## EXAMPLES

  To time the connection and ping times for a Firestore with MongoDB
  compatibility database `testdb`:

      $ {command} --database=testdb
  """

  _NUM_CONNECTS = 5
  _NUM_PINGS = 10

  @staticmethod
  def Args(parser):
    flags.AddDatabaseIdFlag(parser, required=True)

  def Run(self, args):
    project = properties.VALUES.core.project.Get(required=True)
    db = databases.GetDatabase(project, args.database)
    hostname = f'{db.uid}.{db.locationId}.firestore.goog'

    timing_results = []
    print(f'Testing connectivity latency to {hostname}.')
    for _ in range(self._NUM_CONNECTS):
      try:
        timing_results.append(
            connection_util.ConnectAndPing(hostname, self._NUM_PINGS)
        )
      except IOError as e:
        print(f'Failed to establish connection to {hostname}: {e}')
        time.sleep(1)

    # Compute the timing statistics and build the output summary.
    connect_times = list(
        filter(None, [result[0] for result in timing_results if result])
    )
    connection_time_avg = (
        f'{sum(connect_times) / len(connect_times):.3f}'
        if connect_times
        else 'N/A'
    )
    ping_time_lists = [result[1] for result in timing_results if result]
    ping_times = list(
        filter(None, itertools.chain.from_iterable(ping_time_lists))
    )
    ping_time_avg = (
        f'{sum(ping_times) / len(ping_times):.3f}' if ping_times else 'N/A'
    )
    ping_time_stddev = (
        f'{statistics.stdev(ping_times):.3f}' if len(ping_times) > 1 else 'N/A'
    )
    summary = f"""
    Successful connections: {len(connect_times)} / {self._NUM_CONNECTS}
    Average connection setup latency (s): {connection_time_avg}
    Successful pings: {len(ping_times)} / {self._NUM_PINGS * self._NUM_CONNECTS}
    Ping time average (s): {ping_time_avg}
    Ping time standard deviation (s): {ping_time_stddev}
    """
    print(textwrap.dedent(summary))
