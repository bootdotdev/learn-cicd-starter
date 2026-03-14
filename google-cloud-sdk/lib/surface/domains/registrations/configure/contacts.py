# -*- coding: utf-8 -*- #
# Copyright 2020 Google LLC. All Rights Reserved.
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
"""`gcloud domains registrations configure contacts` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.domains import registrations
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.domains import contacts_util
from googlecloudsdk.command_lib.domains import flags
from googlecloudsdk.command_lib.domains import resource_args
from googlecloudsdk.command_lib.domains import util
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
class ConfigureContacts(base.UpdateCommand):
  """Configure contact settings of a Cloud Domains registration.

  Configure registration's contact settings: email, phone number, postal
  address and also contact privacy.

  In some cases such changes have to be confirmed through an email sent to
  the registrant before they take effect. In order to resend the email, execute
  this command again.

  NOTE: Please consider carefully any changes to contact privacy settings when
  changing from "redacted-contact-data" to "public-contact-data."
  There may be a delay in reflecting updates you make to registrant
  contact information such that any changes you make to contact privacy
  (including from "redacted-contact-data" to "public-contact-data")
  will be applied without delay but changes to registrant contact
  information may take a limited time to be publicized. This means that
  changes to contact privacy from "redacted-contact-data" to
  "public-contact-data" may make the previous registrant contact
  data public until the modified registrant contact details are published.

  ## EXAMPLES

  To start an interactive flow to configure contact settings for
  ``example.com'', run:

    $ {command} example.com

  To enable contact privacy for ``example.com'', run:

    $ {command} example.com --contact-privacy=private-contact-data

  To change contact data for ``example.com'' according to information from a
  YAML file ``contacts.yaml'', run:

    $ {command} example.com --contact-data-from-file=contacts.yaml
  """

  @staticmethod
  def Args(parser):
    resource_args.AddRegistrationResourceArg(
        parser, 'to configure contact settings for')
    flags.AddConfigureContactsSettingsFlagsToParser(parser)
    flags.AddValidateOnlyFlagToParser(parser,
                                      'configure contact settings of the')
    flags.AddAsyncFlagToParser(parser)

  def CheckPendingContacts(self, client, registration_ref):
    registration = client.Get(registration_ref)
    return bool(registration.pendingContactSettings)

  def Run(self, args):
    api_version = registrations.GetApiVersionFromArgs(args)
    client = registrations.RegistrationsClient(api_version)
    args.registration = util.NormalizeResourceName(args.registration)
    registration_ref = args.CONCEPTS.registration.Parse()

    registration = client.Get(registration_ref)
    util.AssertRegistrationOperational(api_version, registration)

    contacts = contacts_util.ParseContactData(api_version,
                                              args.contact_data_from_file)
    contact_privacy = contacts_util.ParseContactPrivacy(api_version,
                                                        args.contact_privacy)
    public_contacts_ack = contacts_util.ParsePublicContactsAck(
        api_version, args.notices)

    if contacts is None:
      contacts = contacts_util.PromptForContacts(api_version,
                                                 registration.contactSettings)

    if contact_privacy is None:
      choices = list(
          map(
              flags.ContactPrivacyEnumMapper(client.messages).GetChoiceForEnum,
              registration.supportedPrivacy))
      contact_privacy = contacts_util.PromptForContactPrivacy(
          api_version, choices, registration.contactSettings.privacy)

    if contacts is None and contact_privacy is None:
      # Nothing to update.
      return None

    new_privacy = contact_privacy or registration.contactSettings.privacy
    privacy = client.messages.ContactSettings.PrivacyValueValuesEnum
    if not public_contacts_ack and new_privacy == privacy.PUBLIC_CONTACT_DATA:
      merged_contacts = contacts_util.MergeContacts(
          api_version,
          prev_contacts=registration.contactSettings,
          new_contacts=contacts)
      if registration.contactSettings.privacy != privacy.PUBLIC_CONTACT_DATA:
        public_contacts_ack = contacts_util.PromptForPublicContactsUpdateAck(
            registration.domainName, merged_contacts)
      else:
        public_contacts_ack = contacts_util.PromptForPublicContactsAck(
            registration.domainName, merged_contacts)

    response = client.ConfigureContacts(
        registration_ref,
        contacts,
        contact_privacy,
        public_contacts_ack,
        validate_only=args.validate_only)

    if args.validate_only:
      log.status.Print('The command will not have any effect because '
                       'validate-only flag is present.')
    else:
      response = util.WaitForOperation(api_version, response, args.async_)
      note = None
      if not args.async_ and self.CheckPendingContacts(client,
                                                       registration_ref):
        note = ('Note:\nThe contact settings are currently pending.\nIn order '
                'to finalize the update you need to confirm the change.\nAn '
                'email with instructions has been sent to the registrant.')
      log.UpdatedResource(
          registration_ref.Name(), 'registration', args.async_, details=note)

    return response
