#!/usr/bin/env python
"""Utilities to load Google Auth credentials from gcloud."""

import datetime
import logging
import subprocess
from typing import Iterator, List, Optional

from google.oauth2 import credentials as google_oauth2

import bq_auth_flags
import bq_flags
import bq_utils
from auth import utils as bq_auth_utils
from gcloud_wrapper import gcloud_runner
from utils import bq_error
from utils import bq_gcloud_utils

ERROR_TEXT_PRODUCED_IF_GCLOUD_NOT_FOUND = "No such file or directory: 'gcloud'"

_GDRIVE_SCOPE = 'https://www.googleapis.com/auth/drive'
_GCP_SCOPE = 'https://www.googleapis.com/auth/cloud-platform'


def LoadCredential() -> google_oauth2.Credentials:
  """Loads credentials by calling gcloud commands."""
  gcloud_config = bq_gcloud_utils.load_config()
  account = gcloud_config.get('core', {}).get('account', '')
  logging.info('Loading auth credentials from gcloud for account: %s', account)

  is_service_account = bq_utils.IsServiceAccount(account)
  access_token = _GetAccessTokenAndPrintOutput(is_service_account)
  # Service accounts use the refresh_handler instead of the token for refresh.
  refresh_token = (
      None if is_service_account else _GetRefreshTokenAndPrintOutput()
  )
  refresh_handler = (
      _ServiceAccountRefreshHandler if is_service_account else None
  )
  fallback_quota_project_id = _GetFallbackQuotaProjectId(
      is_service_account=is_service_account,
      has_refresh_token=refresh_token is not None,
  )

  return google_oauth2.Credentials(
      account=account,
      token=access_token,
      refresh_token=refresh_token,
      refresh_handler=refresh_handler,
      client_id=bq_auth_utils.get_client_id(),
      client_secret=bq_auth_utils.get_client_secret(),
      token_uri=bq_auth_utils.get_token_uri(),
      quota_project_id=bq_utils.GetResolvedQuotaProjectID(
          bq_auth_flags.QUOTA_PROJECT_ID.value, fallback_quota_project_id
      ),
  )


def _GetScopes() -> List[str]:
  scopes = []
  if bq_flags.ENABLE_GDRIVE.value:
    drive_scope = _GDRIVE_SCOPE
    scopes.extend([drive_scope, _GCP_SCOPE])
  return scopes


def _GetAccessTokenAndPrintOutput(
    is_service_account: bool, scopes: Optional[List[str]] = None
) -> Optional[str]:
  scopes = _GetScopes() if scopes is None else scopes
  if is_service_account and scopes:
    return _GetTokenFromGcloudAndPrintOtherOutput(
        ['auth', 'print-access-token', '--scopes', ','.join(scopes)]
    )
  return _GetTokenFromGcloudAndPrintOtherOutput(['auth', 'print-access-token'])


def _GetRefreshTokenAndPrintOutput() -> Optional[str]:
  return _GetTokenFromGcloudAndPrintOtherOutput(['auth', 'print-refresh-token'])


def _GetTokenFromGcloudAndPrintOtherOutput(
    cmd: List[str],
    stderr: Optional[int] = subprocess.STDOUT,
) -> Optional[str]:
  """Returns a token or prints other messages from the given gcloud command."""
  try:
    token = None
    for output in _RunGcloudCommand(cmd, stderr):
      if output and ' ' not in output:
        # Token is a non-empty string of non-space characters.
        token = output
        break
      else:
        print(output)
    return token
  except bq_error.BigqueryError as e:
    single_line_error_msg = str(e).replace('\n', '')
    if 'security key' in single_line_error_msg:
      raise bq_error.BigqueryError(
          'Access token has expired. Did you touch the security key within the'
          ' timeout window?\n'
          + _GetReauthMessage()
      )
    elif 'Refresh token has expired' in single_line_error_msg:
      raise bq_error.BigqueryError(
          'Refresh token has expired. ' + _GetReauthMessage()
      )
    elif 'do not support refresh tokens' in single_line_error_msg:
      # It's expected that certain credential types don't support refresh token.
      return None
    else:
      raise bq_error.BigqueryError(
          'Error retrieving auth credentials from gcloud: %s'
          % _UpdateReauthMessage(str(e))
      )
  except Exception as e:  # pylint: disable=broad-exception-caught
    single_line_error_msg = str(e).replace('\n', '')
    if ERROR_TEXT_PRODUCED_IF_GCLOUD_NOT_FOUND in single_line_error_msg:
      raise bq_error.BigqueryError(
          "'gcloud' not found but is required for authentication. To install,"
          ' follow these instructions:'
          ' https://cloud.google.com/sdk/docs/install'
      )
    raise bq_error.BigqueryError(
        'Error retrieving auth credentials from gcloud: %s' % str(e)
    )


def _RunGcloudCommand(
    cmd: List[str], stderr: Optional[int] = subprocess.STDOUT
) -> Iterator[str]:
  """Runs the given gcloud command, yields the output, and returns the final status code."""
  proc = gcloud_runner.run_gcloud_command(cmd, stderr=stderr)
  error_msgs = []
  if proc.stdout:
    for stdout_line in iter(proc.stdout.readline, ''):
      line = str(stdout_line).strip()
      if line.startswith('ERROR:') or error_msgs:
        error_msgs.append(line)
      else:
        yield line
    proc.stdout.close()
  return_code = proc.wait()
  if return_code:
    raise bq_error.BigqueryError('\n'.join(error_msgs))


def _GetReauthMessage() -> str:
  gcloud_command = '$ gcloud auth login' + (
      ' --enable-gdrive-access' if bq_flags.ENABLE_GDRIVE.value else ''
  )
  return 'To re-authenticate, run:\n\n%s' % gcloud_command


def _UpdateReauthMessage(message: str) -> str:
  if '$ gcloud auth login' not in message or not bq_flags.ENABLE_GDRIVE.value:
    return message
  return message.replace(
      '$ gcloud auth login',
      '$ gcloud auth login --enable-gdrive-access',
  )


def _GetFallbackQuotaProjectId(
    is_service_account: bool, has_refresh_token: bool
) -> Optional[str]:
  # When the credential type is not a service account - determined by the
  # account name or whether we can get a non-empty refresh token - set a
  # fallback quota project ID to be the resource project ID. When the credential
  # type is a service account, don't set any fallback quota project ID.
  if is_service_account:
    return None
  if not has_refresh_token:
    return None
  return bq_flags.PROJECT_ID.value


def _ServiceAccountRefreshHandler(request, scopes):
  """Refreshes the access token for a service account."""
  del request  # Unused.
  access_token = _GetAccessTokenAndPrintOutput(
      is_service_account=True, scopes=scopes
  )
  # According to
  # https://cloud.google.com/docs/authentication/token-types#at-lifetime
  # and https://cloud.google.com/sdk/gcloud/reference/auth/print-access-token,
  # the access token lifetime from gcloud auth print-access-token is 1 hour,
  # but set token expiry to 55 minutes from now to be safe.
  expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
      minutes=55
  )
  expiry = expiry.replace(tzinfo=None)
  return access_token, expiry
