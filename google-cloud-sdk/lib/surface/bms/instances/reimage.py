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
"""Bare Metal Solution instance reimage command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.bms.bms_client import BmsClient
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.bms import flags
from googlecloudsdk.core import log
from googlecloudsdk.core import resources

DETAILED_HELP = {
    'DESCRIPTION': """
          Reimage a Bare Metal Solution instance.

          This call returns immediately, but the reimage operation may take
          several minutes to complete. To check if the operation is complete,
          use the `describe` command for the instance.
        """,
    'EXAMPLES': """
          To reimage an instance called ``my-instance'' in region ``us-central1'' with
          the OS image code ``RHEL9x'', run:

          $ {command} my-instance  --region=us-central1 --os-image=RHEL9x

          To set KMS key and ssh keys in order to connect the instance.
          Please use corresponding flags:

          $ {command} my-instance  --region=us-central1 --os-image=RHEL9x --ssh-keys=ssh-key-1,ssh-key-2 --kms-key-version=sample-kms-key-version
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Reimage(base.UpdateCommand):
  """Reimage a Bare Metal Solution instance."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.AddInstanceArgToParser(parser, positional=True)
    base.ASYNC_FLAG.AddToParser(parser)
    flags.AddInstanceOsImageToParser(parser, hidden=False, required=True)
    flags.AddKMSCryptoKeyVersionToParser(parser, hidden=False)
    flags.AddSshKeyArgToParser(
        parser, positional=False, required=False, plural=True
    )

  def Run(self, args):
    client = BmsClient()
    instance = args.CONCEPTS.instance.Parse()
    op_ref = client.ReimageInstance(
        instance,
        os_image=args.os_image,
        ssh_keys=args.CONCEPTS.ssh_keys.Parse(),
        kms_crypto_key_version=getattr(args, 'kms_crypto_key_version', None),
    )
    if op_ref.done:
      log.UpdatedResource(instance.Name(), kind='instance')
      return op_ref
    if args.async_:
      log.status.Print(
          f'Reimage request issued for: [{instance.Name()}]\n'
          f'Check operation [{op_ref.name}] for status.'
      )
      return op_ref
    op_resource = resources.REGISTRY.ParseRelativeName(
        op_ref.name,
        collection='baremetalsolution.projects.locations.operations',
        api_version='v2',
    )

    poller = waiter.CloudOperationPollerNoResources(client.operation_service)
    res = waiter.WaitFor(
        poller,
        op_resource,
        'Waiting for operation [{}] to complete'.format(op_ref.name),
    )
    log.UpdatedResource(instance.Name(), kind='instance')
    return res


Reimage.detailed_help = DETAILED_HELP
