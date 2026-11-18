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

"""The command group for the PAM Grants CLI."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
@base.UniverseCompatible
class AlphaBetaGrants(base.Group):
  r"""Manage Privileged Access Manager (PAM) grants.

  The `gcloud pam grants` command group lets you manage Privileged Access
  Manager (PAM) grants.

  ## EXAMPLES

  To create a new grant against an entitlement with the full name
  ``ENTITLEMENT_NAME'', a requested duration of `1 hour 30 minutes`, a
  justification of `some justification`, and two additional email recipients
  `abc@example.com` and `xyz@example.com`, run:

      $ {command} create --entitlement=ENTITLEMENT_NAME
      --requested-duration=5400s
      --justification="some justification"
      --additional-email-recipients=abc@example.com,xyz@example.com

  To describe a grant with the full name ``GRANT_NAME'', run:

      $ {command} describe GRANT_NAME

  To list all grants associated with an entitlement with the full name
  ``ENTITLEMENT_NAME'', run:

      $ {command} list --entitlement=ENTITLEMENT_NAME

  To deny a grant with the full name ``GRANT_NAME'' and a reason
  `denial reason`, run:

      $ {command} deny GRANT_NAME --reason="denial reason"

  To approve a grant with the full name ``GRANT_NAME'' and a reason
  `approval reason`, run:

      $ {command} approve GRANT_NAME --reason="approval reason"

  To revoke a grant with the full name ``GRANT_NAME'' and a reason
  `revoke reason`, run:

      $ {command} revoke GRANT_NAME --reason="revoke reason"

  To search for and list all grants that you have created that are associated
  with an entitlement with the full name ``ENTITLEMENT_NAME'', run:

      $ {command} search --entitlement=ENTITLEMENT_NAME
      --caller-relationship=had-created

  To search for and list all grants that you have approved or denied, that are
  associated with an entitlement with the full name ``ENTITLEMENT_NAME'', run:

      $ {command} search --entitlement=ENTITLEMENT_NAME
      --caller-relationship=had-approved

  To search for and list all grants that you can approve that are associated
  with an entitlement with the full name ``ENTITLEMENT_NAME'', run:

      $ {command} search --entitlement=ENTITLEMENT_NAME
      --caller-relationship=can-approve

  To withdraw a grant with the full name ``GRANT_NAME'', run:

      $ {command} withdraw GRANT_NAME
  """


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class GAGrants(AlphaBetaGrants):
  r"""Manage Privileged Access Manager (PAM) grants.

  The `gcloud pam grants` command group lets you manage Privileged Access
  Manager (PAM) grants.

  ## EXAMPLES

  To create a new grant against an entitlement with the full name
  ``ENTITLEMENT_NAME'', a requested duration of `1 hour 30 minutes`, a
  justification of `some justification`, and two additional email recipients
  `abc@example.com` and `xyz@example.com`, run:

      $ {command} create --entitlement=ENTITLEMENT_NAME
      --requested-duration=5400s
      --justification="some justification"
      --additional-email-recipients=abc@example.com,xyz@example.com

  To describe a grant with the full name ``GRANT_NAME'', run:

      $ {command} describe GRANT_NAME

  To list all grants associated with an entitlement with the full name
  ``ENTITLEMENT_NAME'', run:

      $ {command} list --entitlement=ENTITLEMENT_NAME

  To deny a grant with the full name ``GRANT_NAME'' and a reason
  `denial reason`, run:

      $ {command} deny GRANT_NAME --reason="denial reason"

  To approve a grant with the full name ``GRANT_NAME'' and a reason
  `approval reason`, run:

      $ {command} approve GRANT_NAME --reason="approval reason"

  To revoke a grant with the full name ``GRANT_NAME'' and a reason
  `revoke reason`, run:

      $ {command} revoke GRANT_NAME --reason="revoke reason"

  To search for and list all grants that you have created that are associated
  with an entitlement with the full name ``ENTITLEMENT_NAME'', run:

      $ {command} search --entitlement=ENTITLEMENT_NAME
      --caller-relationship=had-created

  To search for and list all grants that you have approved or denied, that are
  associated with an entitlement with the full name ``ENTITLEMENT_NAME'', run:

      $ {command} search --entitlement=ENTITLEMENT_NAME
      --caller-relationship=had-approved

  To search for and list all grants that you can approve that are associated
  with an entitlement with the full name ``ENTITLEMENT_NAME'', run:

      $ {command} search --entitlement=ENTITLEMENT_NAME
      --caller-relationship=can-approve

  """
