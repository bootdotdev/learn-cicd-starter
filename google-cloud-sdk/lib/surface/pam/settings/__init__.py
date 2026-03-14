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

"""The command group for the PAM Settings CLI."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Settings(base.Group):
  r"""Manage Privileged Access Manager (PAM) Settings.

  The `gcloud pam settings` command group lets you manage Privileged
  Access Manager (PAM) settings.

  ## EXAMPLES

  To describe the PAM Settings on a project named `sample-project` and
  in location `global`, run:

      $ {command} describe --project=sample-project --location=global

  To describe the PAM Settings on a folder with ID ``FOLDER_ID'' and in
  location `global`, run:

      $ {command} describe --folder=FOLDER_ID --location=global

  To describe the PAM Settings on an organization with ID ``ORGANIZATION_ID''
  and in location `global`, run:

      $ {command} describe --organization=ORGANIZATION_ID --location=global

  To describe the effective PAM Settings on a project named `sample-project` and
  in location `global`, run:

      $ {command} describe-effective --project=sample-project --location=global

  To describe the effective PAM Settings on a folder with ID ``FOLDER_ID'' and
  in location `global`, run:

      $ {command} describe-effective --folder=FOLDER_ID --location=global

  To describe the effective PAM Settings on an organization with ID
  ``ORGANIZATION_ID'' and in location `global`, run:

      $ {command} describe-effective --organization=ORGANIZATION_ID
      --location=global

  To export the PAM Settings configured on a project named `sample-project`,
  and in location `global` to a local YAML file named
  `pam-settings.yaml`, run:

      $ {command} export --project=sample-project --location=global
      --destination=pam-settings.yaml

  To export the PAM Settings configured on a folder with ID ``FOLDER_ID'', and
  in location `global` to a local YAML file named
  `pam-settings.yaml`, run:

      $ {command} export --folder=FOLDER_ID --location=global
      --destination=pam-settings.yaml

  To export the PAM settings configured for an organization with ID
  `ORGANIZATION_ID` in location `global` to a local YAML file named
  `pam-settings.yaml`, run:

      $ {command} export --organization=ORGANIZATION_ID --location=global
        --destination=pam-settings.yaml

  To update the PAM Settings on a project named `sample-project` and in
  location `global`, and the new updated settings configuration stored in a file
  named `pam-settings.yaml`, run:

      $ {command} update --project=sample-project --location=global
      --settings-file=pam-settings.yaml

  To update the PAM Settings on a folder with ID ``FOLDER_ID'' and in location
  `global`, and the new updated settings configuration stored in a file named
  `pam-settings.yaml`, run:

      $ {command} update --folder=FOLDER_ID --location=global
      --settings-file=pam-settings.yaml

  To update the PAM Settings on an organization with ID ``ORGANIZATION_ID'' and
  in location `global`, and the new updated settings configuration stored in a
  file named `pam-settings.yaml`, run:

      $ {command} update --organization=ORGANIZATION_ID --location=global
      --settings-file=pam-settings.yaml
  """
