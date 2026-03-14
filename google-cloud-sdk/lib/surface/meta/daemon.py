# -*- coding: utf-8 -*- #
# Copyright 2025 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The `gcloud meta daemon` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import http.server
import json
import logging
import os
import socketserver
import sys
import time

from googlecloudsdk import gcloud_main
from googlecloudsdk.calliope import base
from googlecloudsdk.core.util import files

# --- Configuration ---
HOST = '0.0.0.0'
PORT = 8080
PRECOMPUTE_DATA = os.environ.get(
    'GCLOUD_DAEMON_PRECOMPUTE_DATA', 'CLI'
)  # or SURFACES or COMMANDS


def perform_gcloud_execution(cli_obj, command_list):
  """Executes the gcloud command using the precomputed CLI object."""
  start_time = time.time()
  pid = os.getpid()  # Current process PID
  logging.info(
      "PID: %s - Starting perform_gcloud_execution with input: '%s'",
      pid,
      command_list,
  )

  if cli_obj is None:
    logging.error('PID: %s - Precomputed CLI object is None!', pid)
    return {'error': 'Internal Server Error: CLI object not available'}

  try:
    request = cli_obj.Execute(command_list)
    response_data = {
        'uri': request.uri,
        'method': request.method,
        'headers': {
            k.decode('utf-8'): v.decode('utf-8')
            for k, v in request.headers.items()
        },
        'body': (
            request.body.decode('utf-8')
            if isinstance(request.body, bytes)
            else request.body
        ),
    }
    logging.info('PID: %s - Execution successful.', pid)
    return response_data
  except SystemExit as exc:
    logging.exception('PID: %s - SystemExit processing request: %s', pid, exc)
    exit_code = exc.code if isinstance(exc.code, int) else 1
    return {
        'error': 'Command failed with SystemExit: %s' % exc,
        'exit_code': exit_code,
    }
  except Exception as e:  # pylint: disable=broad-exception-caught
    logging.error('PID: %s - Exception during command execution:', pid)
    return {'error': 'Exception during command execution: %s' % str(e)}
  finally:
    end_time = time.time()
    computation_time = end_time - start_time
    logging.info(
        'PID: %s - Completed perform_gcloud_execution in %.4f seconds',
        pid,
        computation_time,
    )


@base.Hidden
@base.DefaultUniverseOnly
class Daemon(base.Command):
  """(DEBUG MODE) Precomputes gcloud CLI and runs a single-request server."""

  detailed_help = {
      'DESCRIPTION': """
            (DEBUG MODE) Initializes the gcloud CLI environment based on PRECOMPUTE_DATA,
            starts an HTTP server in the FOREGROUND, serves exactly one POST
            request to the root path ('/'), executes the requested gcloud command
            using the precomputed environment, returns the result, and then exits.

            The command will BLOCK until the single request is received and processed.
        """,
      'EXAMPLES': """
            To run the foreground daemon precomputing the basic CLI:

            $ gcloud meta daemon

            (The command will now wait here)

            Open another terminal and send a request (e.g., using curl):

            $ curl -X POST -H "Content-Type: application/json" -d '{"command_list": ["projects", "list", "--limit=1", "--format=json"]}' http://localhost:8080/

            (The original 'gcloud meta daemon' command will process this, print logs, and then exit)
        """,
  }

  def Run(self, args):
    # Configure logging for the main foreground process
    # pid = os.getpid()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - PID: %(process)d - %(levelname)s - %(message)s',
    )

    # --- Precompute CLI in this main process ---
    logging.info('Starting precomputation...')
    precomputation_start_time = time.time()
    try:
      # Set SDK properties needed for precomputation/execution
      os.environ['CLOUDSDK_CORE_DRY_RUN'] = '1'
      os.environ['CLOUDSDK_AUTH_DISABLE_CREDENTIALS'] = '1'
      os.environ['CLOUDSDK_CORE_DISABLE_PROMPTS'] = '1'
      os.environ['CLOUDSDK_CORE_DISABLE_USAGE_REPORTING'] = '1'
      os.environ['CLOUDSDK_COMPONENT_MANAGER_DISABLE_UPDATE_CHECK'] = '1'
      os.environ['CLOUDSDK_CORE_DISABLE_FILE_LOGGING'] = '1'
      os.environ['CLOUDSDK_CORE_SHOW_STRUCTURED_LOGS'] = 'always'
      os.environ['CLOUDSDK_CORE_VERBOSITY'] = 'error'
      os.environ['CLOUDSDK_METRICS_ENVIRONMENT'] = 'gaas'
      os.environ['CLOUDSDK_CORE_USER_OUTPUT_ENABLED'] = '0'

      precomputed_cli = gcloud_main.CreateCLI([])

      logging.info('Precomputing basic CLI...')
      logging.info('Loading frequent commands')
      try:
        compute_instances_list_command = [
            'compute',
            'instances',
            'list',
            '--project=fake-project',
        ]
        precomputed_cli.Execute(compute_instances_list_command)
      except Exception:  # pylint: disable=broad-exception-caught
        pass

      precomputation_end_time = time.time()
      logging.info(
          'Precomputation complete in %.4f seconds.',
          precomputation_end_time - precomputation_start_time,
      )
    except Exception as e:  # pylint: disable=broad-exception-caught
      logging.exception('Failed during CLI precomputation:')
      sys.exit('Error during CLI precomputation: %s' % e)

    # --- Define Handler and Start Server ---
    class SingleRequestHandler(http.server.BaseHTTPRequestHandler):
      """Handles ONE incoming POST request and then signals shutdown."""

      # pylint: disable=invalid-name
      def do_POST(self):
        """Handles the single POST request."""
        pid = os.getpid()  # Log current process PID
        logging.info('PID: %s - Request received at path: %s', pid, self.path)

        if self.path == '/':
          content_length = int(self.headers['Content-Length'])
          post_data = self.rfile.read(content_length)
          try:
            request_data = json.loads(post_data.decode('utf-8'))
            command_list = request_data.get('command_list')
            if not command_list or not isinstance(command_list, list):
              logging.error(
                  "PID: %s - Missing or invalid 'command_list' (must be a list)"
                  ' in request',
                  pid,
              )
              self.send_error(
                  400,
                  "Missing or invalid 'command_list' (must be a list) in"
                  ' request',
              )
              return
          except json.JSONDecodeError:
            logging.error('PID: %s - Invalid JSON request', pid, exc_info=True)
            self.send_error(400, 'Invalid JSON request')
            return

          logging.info(
              'PID: %s - Received compute request with command: %s',
              pid,
              command_list,
          )

          # Execute the command using the precomputed CLI
          response_data = perform_gcloud_execution(
              precomputed_cli, command_list
          )

          # Send response
          status_code = 200  # sandbox always returns 200 for IPC
          self.send_response(status_code)
          self.send_header('Content-type', 'application/json')
          self.end_headers()
          self.wfile.write(json.dumps(response_data).encode('utf-8'))
          logging.info('PID: %s - Response sent to client.', pid)

        else:
          logging.warning(
              'PID: %s - Received request for unknown path: %s', pid, self.path
          )
          self.send_error(404)  # Not Found

        # Signal the server's main thread to shut down
        logging.info(
            'PID: %s - Request handled. Signaling server shutdown.', pid
        )

      # pylint: disable=redefined-builtin
      def log_message(self, format, *args):
        """Log messages using the standard logger."""
        # Adjust message slightly for foreground clarity
        logging.info('PID: %s - HTTP Server: %s', os.getpid(), format % args)

    # --- Start HTTP server directly in this process ---
    logging.info('Starting foreground HTTP server...')
    try:
      socketserver.TCPServer.allow_reuse_address = True
      with socketserver.TCPServer((HOST, PORT), SingleRequestHandler) as httpd:
        # Touch a file to signal readiness
        gcloud_daemon_ready_file = '/tmp/gcloud_daemon.ready'
        with files.FileWriter(gcloud_daemon_ready_file) as f:
          f.write('ready')
        logging.info('Created %s', gcloud_daemon_ready_file)
        logging.info(
            'Server started on http://%s:%s (PRECOMPUTE_DATA=%s)',
            HOST,
            PORT,
            PRECOMPUTE_DATA,
        )
        # Process one request (blocks until one arrives) and then exits the
        # 'with' block, which handles shutdown.
        httpd.handle_request()

        logging.info('Request handled. Server shutting down.')
        httpd.server_close()

    except Exception as e:  # pylint: disable=broad-exception-caught
      # Log any exception during server setup or the loop itself
      logging.exception('Unhandled exception occurred in server process:')
      sys.exit('Server error: %s' % e)
    finally:
      logging.info('Server process function exiting.')
      logging.shutdown()  # Flush and close handlers

    logging.info('Daemon command finished normally after serving request.')
    sys.exit(0)  # Ensure clean exit
