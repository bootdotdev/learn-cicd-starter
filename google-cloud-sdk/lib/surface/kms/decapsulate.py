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
"""Decapsulate an input file using a key-encapsulation key version."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.cloudkms import base as cloudkms_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.kms import crc32c
from googlecloudsdk.command_lib.kms import e2e_integrity
from googlecloudsdk.command_lib.kms import flags
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io
from googlecloudsdk.core.util import files


@base.UniverseCompatible
class Decapsulate(base.Command):
  r"""Decapsulate an input file using a key-encapsulation key version.

  Decapsulates the given ciphertext file using the provided key-encapsulation
  key version and saves the decapsulated shared secret to the shared secret file.

  By default, the command performs integrity verification on data sent to and
  received from Cloud KMS. Use `--skip-integrity-verification` to disable
  integrity verification.

  ## EXAMPLES
  The following command will read the file '/tmp/my/secret.file.enc', decapsulate it
  using the key encapsulation CryptoKey `my-key` Version 3 and write the shared secret
  to '/tmp/my/secret.file.dec'.

    $ {command} \
    --location=us-central1 \
    --keyring=my-keyring \
    --key=my-key \
    --version=3 \
    --ciphertext-file=/tmp/my/secret.file.enc \
    --shared-secret-file=/tmp/my/secret.file.dec

  """

  @staticmethod
  def Args(parser):
    flags.AddKeyResourceFlags(parser, 'to use for decapsulation.')
    flags.AddCryptoKeyVersionFlag(parser, 'to use for decapsulation')
    flags.AddCiphertextFileFlag(parser, 'to decapsulate')
    flags.AddSharedSecretFileFlag(parser, 'to output')
    flags.AddSkipIntegrityVerification(parser)

  def _PerformIntegrityVerification(self, args):
    return not args.skip_integrity_verification

  def _CreateDecapsulateRequest(self, args):
    try:
      ciphertext = console_io.ReadFromFileOrStdin(
          args.ciphertext_file, binary=True)
    except files.Error as e:
      raise exceptions.BadFileException(
          'Failed to read ciphertext file [{0}]: {1}'.format(
              args.ciphertext_file, e))

    messages = cloudkms_base.GetMessagesModule()
    crypto_key_ref = flags.ParseCryptoKeyVersionName(args)

    req = messages.CloudkmsProjectsLocationsKeyRingsCryptoKeysCryptoKeyVersionsDecapsulateRequest(  # pylint: disable=line-too-long
        name=crypto_key_ref.RelativeName()
    )
    if self._PerformIntegrityVerification(args):
      ciphertext_crc32c = crc32c.Crc32c(ciphertext)
      req.decapsulateRequest = messages.DecapsulateRequest(
          ciphertext=ciphertext, ciphertextCrc32c=ciphertext_crc32c
      )
    else:
      req.decapsulateRequest = messages.DecapsulateRequest(
          ciphertext=ciphertext
      )

    return req

  def _VerifyResponseIntegrityFields(self, req, resp):
    """Verifies integrity fields in response."""

    # ciphertext_crc32c was verified server-side.
    if not resp.verifiedCiphertextCrc32c:
      raise e2e_integrity.ClientSideIntegrityVerificationError(
          e2e_integrity.GetRequestToServerCorruptedErrorMessage())

    # Verify plaintext checksum.
    if not crc32c.Crc32cMatches(resp.sharedSecret, resp.sharedSecretCrc32c):
      raise e2e_integrity.ClientSideIntegrityVerificationError(
          e2e_integrity.GetResponseFromServerCorruptedErrorMessage())

  def Run(self, args):
    req = self._CreateDecapsulateRequest(args)
    client = cloudkms_base.GetClientInstance()
    try:
      resp = client.projects_locations_keyRings_cryptoKeys_cryptoKeyVersions.Decapsulate(
          req
      )

      if self._PerformIntegrityVerification(args):
        self._VerifyResponseIntegrityFields(req, resp)

      log.WriteToFileOrStdout(
          args.shared_secret_file,
          resp.sharedSecret or '',
          overwrite=True,
          binary=True,
          private=True,
      )

    # Intercept INVALID_ARGUMENT errors related to checksum verification to
    # present a user-friendly message. All other errors are surfaced as-is.
    except apitools_exceptions.HttpBadRequestError as error:
      e2e_integrity.ProcessHttpBadRequestError(error)
    except files.Error as e:
      raise exceptions.BadFileException(e)
