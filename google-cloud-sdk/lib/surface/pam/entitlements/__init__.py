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

"""The command group for the PAM Entitlements CLI."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base


@base.ReleaseTracks(base.ReleaseTrack.ALPHA,
                    base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
@base.UniverseCompatible
class Entitlements(base.Group):
  r"""Manage Privileged Access Manager (PAM) entitlements.

  The `gcloud pam entitlements` command group lets you manage Privileged Access
  Manager (PAM) entitlements.

  ## EXAMPLES

  To create a new entitlement with a name of `sample-entitlement`, in a project
  named `sample-project`, in location `global`, and the entitlement
  configuration stored in a file named `sample-entitlement.yaml`, run:

      $ {command} create sample-entitlement --project=sample-project
      --location=global --entitlement-file=sample-entitlement.yaml

  To create a new entitlement with a name of `sample-entitlement`, in a folder
  with ID ``FOLDER_ID'', in location `global`, and the entitlement
  configuration stored in a file named `sample-entitlement.yaml`, run:

      $ {command} create sample-entitlement --folder=FOLDER_ID
      --location=global --entitlement-file=sample-entitlement.yaml

  To create a new entitlement with a name of `sample-entitlement`, in an
  organization with ID ``ORGANIZATION_ID'', in location `global`, and the
  entitlement configuration stored in a file named `sample-entitlement.yaml`,
  run:

      $ {command} create sample-entitlement --organization=ORGANIZATION_ID
      --location=global --entitlement-file=sample-entitlement.yaml

  To update an entitlement with a name of `sample-entitlement`, in a project
  named `sample-project`, in location `global`, and the new entitlement
  configuration stored in a file named `sample-entitlement.yaml`, run:

      $ {command} update sample-entitlement --project=sample-project
      --location=global --entitlement-file=sample-entitlement.yaml

  To update an entitlement with a name of `sample-entitlement`, in a folder
  with ID ``FOLDER_ID'', in location `global`, and the new entitlement
  configuration stored in a file named `sample-entitlement.yaml`, run:

      $ {command} update sample-entitlement --folder=FOLDER_ID
      --location=global --entitlement-file=sample-entitlement.yaml

  To update an entitlement with a name of `sample-entitlement`, in an
  organization with ID ``ORGANIZATION_ID'', in location `global`, and the new
  entitlement configuration stored in a file named `sample-entitlement.yaml`,
  run:

      $ {command} update sample-entitlement --organization=ORGANIZATION_ID
      --location=global --entitlement-file=sample-entitlement.yaml

  To describe an entitlement with a name of `sample-entitlement`, in a project
  named `sample-project`, and in location `global`, run:

      $ {command} describe sample-entitlement --project=sample-project
      --location=global

  To describe an entitlement with a name of `sample-entitlement`, in a folder
  with ID ``FOLDER_ID'', and in location `global`, run:

      $ {command} describe sample-entitlement --folder=FOLDER_ID
      --location=global

  To describe an entitlement with a name of `sample-entitlement`, in an
  organization with ID ``ORGANIZATION_ID'', and in location `global`, run:

      $ {command} describe sample-entitlement --organization=ORGANIZATION_ID
      --location=global

  To search for and list all entitlements for which you are a requester, in a
  project named `sample-project`, and in location `global`, run:

      $ {command} search --project=sample-project --location=global
      --caller-access-type=grant-requester

  To search for and list all entitlements for which you are an approver, in a
  project named `sample-project`, and in location `global`, run:

      $ {command} search --project=sample-project --location=global
      --caller-access-type=grant-approver

  To search for and list all entitlements for which you are a requester, in a
  folder with ID ``FOLDER_ID'', and in location `global`, run:

      $ {command} search --folder=FOLDER_ID --location=global
      --caller-access-type=grant-requester

  To search for and list all entitlements for which you are an approver, in a
  folder with ID ``FOLDER_ID'', and in location `global`, run:

      $ {command} search --folder=FOLDER_ID --location=global
      --caller-access-type=grant-approver

  To search for and list all entitlements for which you are a requester, in an
  organization with ID ``ORGANIZATION_ID'', and in location `global`, run:

      $ {command} search --organization=ORGANIZATION_ID --location=global
      --caller-access-type=grant-requester

  To search for and list all entitlements for which you are an approver, in an
  organization with ID ``ORGANIZATION_ID'', and in location `global`, run:

      $ {command} search --organization=ORGANIZATION_ID --location=global
      --caller-access-type=grant-approver

  To list all entitlements in a project named `sample-project` and in location
  `global`, run:

      $ {command} list --project=sample-project --location=global

  To list all entitlements in a folder with ID ``FOLDER_ID'' and in location
  `global`, run:

      $ {command} list --folder=FOLDER_ID --location=global

  To list all entitlements in an organization with ID ``ORGANIZATION_ID'' and
  in location `global`, run:

      $ {command} list --organization=ORGANIZATION_ID --location=global

  To delete an entitlement with a name of `sample-entitlement`, in a project
  named `sample-project`, and in location `global`, run:

      $ {command} delete sample-entitlement --project=sample-project
      --location=global

  To delete an entitlement with a name of `sample-entitlement`, in a folder
  with ID ``FOLDER_ID'', and in location `global`, run:

      $ {command} delete sample-entitlement --folder=FOLDER_ID
      --location=global

  To delete an entitlement with a name of `sample-entitlement`, in an
  organization with ID ``ORGANIZATION_ID'', and in location `global`, run:

      $ {command} delete sample-entitlement --organization=ORGANIZATION_ID
      --location=global

  To export an entitlement with a name of `sample-entitlement`, in a project
  named `sample-project`, and in location `global` to a local YAML file named
  `sample-entitlement.yaml`, run:

      $ {command} export sample-entitlement --project=sample-project
      --location=global --destination=sample-entitlement.yaml

  To export an entitlement with a name of `sample-entitlement`, in a folder
  with ID ``FOLDER_ID'', and in location `global` to a local YAML file named
  `sample-entitlement.yaml`, run:

      $ {command} export sample-entitlement --folder=FOLDER_ID
      --location=global --destination=sample-entitlement.yaml

  To export an entitlement with a name of `sample-entitlement`, in an
  organization with ID ``ORGANIZATION_ID'', and in location `global` to a local
  YAML file named `sample-entitlement.yaml`, run:

      $ {command} export sample-entitlement --organization=ORGANIZATION_ID
      --location=global --destination=sample-entitlement.yaml
  """
