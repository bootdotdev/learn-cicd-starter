# -*- coding: utf-8 -*- #
# Copyright 2017 Google LLC. All Rights Reserved.
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
"""Get the public key for a given version."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.cloudkms import base as cloudkms_base
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.kms import flags
from googlecloudsdk.command_lib.kms import maps
from googlecloudsdk.core import log


@base.UniverseCompatible
class GetPublicKey(base.DescribeCommand):
  r"""Get the public key for a given version.

  Returns the public key of the given asymmetric key version in the specified format.

  The optional flag `output-file` indicates the path to store the public key.
  If not specified, the public key will be printed to stdout.

  The optional flag `public-key-format` indicates the format in which the
  public key will be returned. For the NIST PQC algorithms, this must be
  specified and set to `nist-pqc`. For kem-xwing this must be specified and set to
  `xwing-raw-bytes`. For all other algorithms, this flag is
  optional and can be either `pem` or `der`; the default value is `pem`.
  See "Retrieve a public key" in the Cloud KMS
  documentation (https://cloud.google.com/kms/help/get-public-key) for more
  information about the supported formats.

  ## EXAMPLES

  The following command saves the public key for CryptoKey `frodo` Version 2
  to '/tmp/my/public_key.file':

    $ {command} 2 \
    --key=frodo \
    --keyring=fellowship \
    --location=us-east1 \
    --public-key-format=pem \
    --output-file=/tmp/my/public_key.file
  """

  @staticmethod
  def Args(parser):
    flags.AddKeyVersionResourceArgument(parser, 'to get public key')
    flags.AddOutputFileFlag(parser, 'to store public key')
    flags.AddPublicKeyFormatFlag(parser)

  def Run(self, args):
    client = cloudkms_base.GetClientInstance()
    messages = cloudkms_base.GetMessagesModule()

    version_ref = flags.ParseCryptoKeyVersionName(args)
    if not version_ref.Name():
      raise exceptions.InvalidArgumentException(
          'version', 'version id must be non-empty.'
      )
    req = messages.CloudkmsProjectsLocationsKeyRingsCryptoKeysCryptoKeyVersionsGetPublicKeyRequest(  # pylint: disable=line-too-long
        name=version_ref.RelativeName(),
    )
    if args.public_key_format:
      if args.public_key_format not in [
          'pem',
          'der',
          'nist-pqc',
          'xwing-raw-bytes',
      ]:
        raise exceptions.InvalidArgumentException(
            '--public-key-format',
            'Invalid value for public key format. Supported values are "der",'
            ' "pem", "xwing-raw-bytes" and "nist-pqc".',
        )
      req.publicKeyFormat = maps.PUBLIC_KEY_FORMAT_MAPPER.GetEnumForChoice(
          args.public_key_format
      )
    resp = client.projects_locations_keyRings_cryptoKeys_cryptoKeyVersions.GetPublicKey(
        req
    )

    # DER, NIST_PQC and XWING_RAW_BYTES are in raw byte format.
    # So the output is in binary format.
    write_binary_file = args.public_key_format in [
        'der',
        'nist-pqc',
        'xwing-raw-bytes',
    ]
    log.WriteToFileOrStdout(
        args.output_file if args.output_file else '-',
        resp.pem if resp.pem else resp.publicKey.data,
        overwrite=True,
        binary=write_binary_file,
        private=True,
    )
