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

"""The command group for the profiles CLI."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.projects import util


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Profiles(base.Group):
  """Quickstart engine for GKE AI workloads.

  The GKE Inference Quickstart helps simplify deploying AI inference on Google
  Kubernetes Engine (GKE). It provides tailored profiles based on
  Google's internal benchmarks. Provide inputs like your preferred open-source
  model (e.g. Llama, Gemma, or Mistral) and your application's performance
  target. Based on these inputs, the quickstart generates accelerator choices
  with performance metrics, and detailed, ready-to-deploy profiles for
  compute, load balancing, and autoscaling. These profiles are provided
  as standard Kubernetes YAML manifests, which you can deploy or modify.

  To visualize the benchmarking data that support these estimates, see the
  accompanying Colab notebook:
  https://colab.research.google.com/github/GoogleCloudPlatform/kubernetes-engine-samples/blob/main/ai-ml/notebooks/giq_visualizations.ipynb
  """

  category = base.SDK_TOOLS_CATEGORY
