# -*- coding: utf-8 -*- #
# Copyright 2015 Google LLC. All Rights Reserved.
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

"""Command to delete named configuration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.config import completers
from googlecloudsdk.core import config
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.configurations import named_configs
from googlecloudsdk.core.configurations import properties_file
from googlecloudsdk.core.console import console_io
from googlecloudsdk.core.resource import resource_printer
from googlecloudsdk.core.universe_descriptor import universe_descriptor


@base.UniverseCompatible
class Delete(base.SilentCommand):
  """Deletes a named configuration."""

  detailed_help = {
      'DESCRIPTION': """\
          {description} You cannot delete a configuration that is active, even
          when overridden with the --configuration flag.  To delete the current
          active configuration, first `gcloud config configurations activate`
          another one.

          See `gcloud topic configurations` for an overview of named
          configurations.
          """,
      'EXAMPLES': """\
          To delete an existing configuration named `my-config`, run:

            $ {command} my-config

          To delete more than one configuration, run:

            $ {command} my-config1 my-config2

          To list existing configurations, run:

            $ gcloud config configurations list
          """,
  }

  @staticmethod
  def Args(parser):
    """Adds args for this command."""
    parser.add_argument(
        'configuration_names',
        nargs='+',
        completer=completers.NamedConfigCompleter,
        help=(
            'Name of the configuration to delete. '
            'Cannot be currently active configuration.'
        ),
    )

  def _UniverseDomainSetInAnyConfig(self, universe_domain: str) -> bool:
    """Determines whether the universe domain is set in any other config.

    Args:
      universe_domain: The universe domain to check for in any other config.

    Returns:
      True if the universe domain is set in any other config, False otherwise.
    """
    all_configs = named_configs.ConfigurationStore.AllConfigs()
    for _, user_config in sorted(all_configs.items()):
      props = properties.VALUES.AllValues(
          list_unset=True,
          include_hidden=True,
          properties_file=properties_file.PropertiesFile(
              [user_config.file_path]
          ),
          only_file_contents=True,
      )
      if props['core'].get('universe_domain') == universe_domain:
        return True
    return False

  def _DeleteUniverseDescriptor(self, universe_domain: str) -> None:
    """Deletes the universe descriptor if it is not used in any other config.

    Args:
      universe_domain: The universe domain of the descriptor to delete.
    """
    universe_descriptor_obj = universe_descriptor.UniverseDescriptor()
    if not self._UniverseDomainSetInAnyConfig(universe_domain):
      universe_descriptor_obj.DeleteDescriptorFromUniverseDomain(
          universe_domain
      )

  def _GetConfigurationUniverseDomain(self, config_name: str) -> str:
    """Returns the universe domain of the given configuration.

    Args:
      config_name: The name of the configuration to get the universe domain of.

    Returns:
      The universe domain of the given configuration or the default if not
      found.
    """
    all_named_configs = named_configs.ConfigurationStore.AllConfigs()
    for _, user_config in sorted(all_named_configs.items()):
      if user_config.name == config_name:
        props = properties.VALUES.AllValues(
            list_unset=True,
            include_hidden=True,
            properties_file=properties_file.PropertiesFile(
                [user_config.file_path]
            ),
            only_file_contents=True,
        )
        return (
            props['core'].get('universe_domain')
            or properties.VALUES.core.universe_domain.default
        )
    return properties.VALUES.core.universe_domain.default

  def Run(self, args):
    # Fail the delete operation when we're attempting to delete the
    # active config.
    active_config = named_configs.ConfigurationStore.ActiveConfig()
    if active_config.name in args.configuration_names:
      raise named_configs.NamedConfigError(
          'Deleting named configuration failed because configuration '
          '[{0}] is set as active.  Use `gcloud config configurations '
          'activate` to change the active configuration.'.format(
              active_config.name
          )
      )

    fmt = 'list[title="The following configurations will be deleted:"]'
    resource_printer.Print(args.configuration_names, fmt, out=log.status)
    console_io.PromptContinue(default=True, cancel_on_no=True)

    for configuration_name in args.configuration_names:
      delete_config_universe_domain = self._GetConfigurationUniverseDomain(
          configuration_name
      )
      named_configs.ConfigurationStore.DeleteConfig(configuration_name)
      config_store_to_delete = config.GetConfigStore(configuration_name)
      config_store_to_delete.DeleteConfig()
      try:
        self._DeleteUniverseDescriptor(delete_config_universe_domain)
      except universe_descriptor.UniverseDescriptorError as e:
        log.warning(
            'Failed to delete universe descriptor for universe domain %s: %s',
            delete_config_universe_domain,
            e,
        )
      log.DeletedResource(configuration_name)
