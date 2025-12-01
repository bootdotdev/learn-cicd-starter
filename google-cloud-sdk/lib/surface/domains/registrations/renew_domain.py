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
"""`gcloud domains registrations renew-domain` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import re

from apitools.base.py import exceptions as apitools_exceptions

from googlecloudsdk.api_lib.domains import registrations
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.domains import flags
from googlecloudsdk.command_lib.domains import resource_args
from googlecloudsdk.command_lib.domains import util
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
class RenewDomain(base.UpdateCommand):
  """Renew a recently expired Cloud Domains registration.

  Use this method to renew domains that expired within the last 30 days.
  Renewing your domain extends it for one year from the previous expiration date
  and you are charged the yearly renewal price.

  ## EXAMPLES

  To renew a registration for ``example.com'' interactively, run:

    $ {command} example.com

  To renew ``example.com'' with interactive prompts disabled, provide the
  --yearly-price flag. For example, run:

    $ {command} example.com --yearly-price="12.00 USD" --quiet
  """

  @staticmethod
  def Args(parser):
    resource_args.AddRegistrationResourceArg(parser, 'to renew')
    flags.AddPriceFlagsToParser(parser, flags.MutationOp.RENEWAL)
    flags.AddValidateOnlyFlagToParser(parser, 'renew')
    flags.AddAsyncFlagToParser(parser)

  def Run(self, args):
    api_version = registrations.GetApiVersionFromArgs(args)
    client = registrations.RegistrationsClient(api_version)
    args.registration = util.NormalizeResourceName(args.registration)
    registration_ref = args.CONCEPTS.registration.Parse()

    yearly_price = util.ParseYearlyPrice(api_version, args.yearly_price)
    if yearly_price is None:
      messages = registrations.GetMessagesModule(api_version)
      empty_price = messages.Money()
      try:
        client.Renew(registration_ref, empty_price, validate_only=True)
      except apitools_exceptions.HttpError as e:
        match = re.search(r'INVALID: expected (\d+).(\d{2}) USD', e.content)
        if match:
          units, cents = match.groups()
          yearly_price = messages.Money(
              units=int(units), nanos=int(cents) * 10**7, currencyCode='USD')
          yearly_price = util.PromptForYearlyPriceAck(yearly_price)
          if yearly_price is None:
            raise exceptions.Error('Accepting yearly price is required.')
        else:
          raise e

    response = client.Renew(registration_ref, yearly_price, args.validate_only)

    if args.validate_only:
      log.status.Print('The command will not have any effect because '
                       'validate-only flag is present.')
    else:
      response = util.WaitForOperation(api_version, response, args.async_)
      log.UpdatedResource(registration_ref.Name(), 'registration', args.async_)
    return response
