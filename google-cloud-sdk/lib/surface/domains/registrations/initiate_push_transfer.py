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
"""`gcloud domains registrations initiate-push-transfer` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.domains import registrations
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.domains import flags
from googlecloudsdk.command_lib.domains import resource_args
from googlecloudsdk.command_lib.domains import util
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
class InitiatePushTransfer(base.UpdateCommand):
  """Initiates the push transfer process.

  Initiates the `Push Transfer` process to transfer the domain to another
  registrar. The process might complete instantly or might require confirmation
  or additional work. Check the emails sent to the email address of the
  registrant. The process is aborted after a timeout if it's not completed.

  This method is only supported for domains that have the
  `REQUIRE_PUSH_TRANSFER` property in the list of `domain_properties`. The
  domain must also be unlocked before it can be transferred to a different
  registrar.

  ## EXAMPLES

  To initiate a push transfer for ``example.co.uk'', run:

    $ {command} example.co.uk --tag=NEW_REGISTRY_TAG
  """

  @staticmethod
  def Args(parser):
    resource_args.AddRegistrationResourceArg(parser, 'to transfer')
    flags.AddTagFlagToParser(parser)
    flags.AddAsyncFlagToParser(parser)

  def Run(self, args):
    api_version = registrations.GetApiVersionFromArgs(args)
    client = registrations.RegistrationsClient(api_version)
    args.registration = util.NormalizeResourceName(args.registration)
    registration_ref = args.CONCEPTS.registration.Parse()

    console_io.PromptContinue(
        ('You are about to start the push transfer process of '
         'registration \'{}\'').format(
             registration_ref.registrationsId),
        throw_if_unattended=True,
        cancel_on_no=True)

    response = client.InitiatePushTransfer(registration_ref, args.tag)

    response = util.WaitForOperation(api_version, response, args.async_)
    log.UpdatedResource(registration_ref.Name(), 'registration', args.async_)
    return response
