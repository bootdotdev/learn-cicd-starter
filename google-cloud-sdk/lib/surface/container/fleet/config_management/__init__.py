# -*- coding: utf-8 -*- #
# Copyright 2022 Google LLC. All Rights Reserved.
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
"""Command group for Config Management Feature."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base as calliope_base


class Configmanagement(calliope_base.Group):
  """Use the Config Management feature."""

  category = calliope_base.COMPUTE_CATEGORY
  # Config Sync link breaks in docstring because it does not fit on 1 line.
  # Pylint disallows long lines, even for a raw docstring, and the use of
  # backslashes.
  detailed_help = {
      'DESCRIPTION': """
Manage
[Config Sync](https://cloud.google.com/kubernetes-engine/config-sync/gcloud-help/manage)
using the Config Management feature.

To manage Policy Controller, use `gcloud container fleet policycontroller`
instead.

Hierarchy Controller is no longer available to install. If Hierarchy Controller
is still configured, Config Sync upgrades are blocked. To upgrade Config Sync,
disable Hierarchy Controller following
https://cloud.google.com/kubernetes-engine/enterprise/config-sync/docs/how-to/migrate-hierarchy-controller.
"""
  }
