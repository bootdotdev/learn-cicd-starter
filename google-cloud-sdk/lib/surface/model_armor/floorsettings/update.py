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
"""Fetch the FloorSetting resource."""

import json

from googlecloudsdk.api_lib.model_armor import api as model_armor_api
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.model_armor import args as model_armor_args
from googlecloudsdk.command_lib.model_armor import util as model_armor_util


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Update(base.Command):
  """Update the FloorSetting resource.

  Updates the floor setting resource with the given name.
  """

  NO_CHANGES_MESSAGE = 'There are no changes to the floor setting for update.'

  @staticmethod
  def Args(parser):
    model_armor_args.AddFullUri(
        parser,
        positional=False,
        required=True,
        help_text='Full uri of the floor setting',
    )
    model_armor_args.AddFloorSettingEnforcement(
        parser,
        positional=False,
        required=False,
        help_text='Enable or disable the floor setting enforcement',
    )
    model_armor_args.AddMaliciousUriFilterSettingsEnforcement(parser)
    model_armor_args.AddPIJBFilterSettingsGroup(parser)
    model_armor_args.AddSDPFilterBasicConfigGroup(parser)
    model_armor_args.AddRaiFilterSettingsGroup(parser)

  def _GetEnumValue(self, value):
    return value.upper().replace('-', '_')

  def _validateRaiFilterSettings(self, messages, filters, argument_name):
    for item in [json.loads(f) for f in filters]:
      confidence_level = item['confidenceLevel']
      filter_type = item['filterType']
      model_armor_util.ValidateEnum(
          filter_type,
          messages.RaiFilter.FilterTypeValueValuesEnum,
          argument_name,
          f'Invalid choice : {filter_type}',
      )
      model_armor_util.ValidateEnum(
          confidence_level,
          messages.RaiFilter.ConfidenceLevelValueValuesEnum,
          argument_name,
          f'Invalid choice : {confidence_level}',
      )

  def _validateArgs(self, messages, args):
    """Validate the arguments."""
    if args.pi_and_jailbreak_filter_settings_confidence_level:
      model_armor_util.ValidateEnum(
          args.pi_and_jailbreak_filter_settings_confidence_level,
          messages.PiAndJailbreakFilterResult.ConfidenceLevelValueValuesEnum,
          'pi-and-jailbreak-filter-settings-confidence-level',
          'Invalid choice :'
          f' {args.pi_and_jailbreak_filter_settings_confidence_level}',
      )
    if args.pi_and_jailbreak_filter_settings_enforcement:
      model_armor_util.ValidateEnum(
          args.pi_and_jailbreak_filter_settings_enforcement,
          messages.PiAndJailbreakFilterSettings.FilterEnforcementValueValuesEnum,
          'pi-and-jailbreak-filter-settings-enforcement',
          'Invalid choice :'
          f' {args.pi_and_jailbreak_filter_settings_enforcement}',
      )
    if args.malicious_uri_filter_settings_enforcement:
      model_armor_util.ValidateEnum(
          args.malicious_uri_filter_settings_enforcement,
          messages.MaliciousUriFilterSettings.FilterEnforcementValueValuesEnum,
          'malicious-uri-filter-settings-enforcement',
          f'Invalid choice : {args.malicious_uri_filter_settings_enforcement}',
      )
    if args.basic_config_filter_enforcement:
      model_armor_util.ValidateEnum(
          args.basic_config_filter_enforcement,
          messages.SdpBasicConfig.FilterEnforcementValueValuesEnum,
          'basic-config-filter-enforcement',
          f'Invalid choice : {args.basic_config_filter_enforcement}',
      )
    if args.rai_settings_filters:
      self._validateRaiFilterSettings(
          messages, args.rai_settings_filters, 'rai-settings-filters'
      )
    if args.add_rai_settings_filters:
      self._validateRaiFilterSettings(
          messages, args.add_rai_settings_filters, 'add-rai-settings-filters'
      )
    if args.remove_rai_settings_filters:
      self._validateRaiFilterSettings(
          messages,
          args.remove_rai_settings_filters,
          'remove-rai-settings-filters',
      )
    if args.IsSpecified('basic_config_filter_enforcement') and ((
        args.IsSpecified('advanced_config_inspect_template')
        or args.IsSpecified('advanced_config_deidentify_template')
    )):
      raise exceptions.ConflictingArgumentsException(
          'basic_config_filter_enforcement', 'sdp_advanced_config_*_template'
      )

  def _RunUpdate(self, original, args):
    api_version = model_armor_api.GetApiFromTrack(self.ReleaseTrack())
    api_client = model_armor_api.FloorSettings(api_version=api_version)
    messages = api_client.GetMessages()
    self._validateArgs(messages, args)
    floor_setting_updated = original

    if floor_setting_updated.filterConfig is None:
      floor_setting_updated.filterConfig = messages.FilterConfig()

    # Collect the list of update masks
    update_mask = []
    if args.IsSpecified(
        'pi_and_jailbreak_filter_settings_enforcement'
    ) or args.IsSpecified('pi_and_jailbreak_filter_settings_confidence_level'):
      update_mask.append('filter_config.pi_and_jailbreak_filter_settings')
    if args.IsSpecified('malicious_uri_filter_settings_enforcement'):
      update_mask.append('filter_config.malicious_uri_filter_settings')
    if (
        args.IsSpecified('basic_config_filter_enforcement')
        or args.IsSpecified('advanced_config_inspect_template')
        or args.IsSpecified('advanced_config_deidentify_template')
    ):
      update_mask.append('filter_config.sdp_settings')
    if (
        args.IsSpecified('add_rai_settings_filters')
        or args.IsSpecified('remove_rai_settings_filters')
        or args.IsSpecified('clear_rai_settings_filters')
        or args.IsSpecified('rai_settings_filters')
    ):
      update_mask.append('filter_config.rai_settings')
    if args.IsSpecified('enable_floor_setting_enforcement'):
      update_mask.append('enable_floor_setting_enforcement')

    if not update_mask:
      raise exceptions.MinimumArgumentException(
          [
              '--pi-and-jailbreak-filter-settings-enforcement',
              '--pi-and-jailbreak-filter-settings-confidence-level',
              '--malicious-uri-filter-settings-enforcement',
              '--basic-config-filter-enforcement',
              '--advanced-config-inspect-template',
              '--advanced-config-deidentify-template',
              '--rai-settings-filters',
              '--add-rai-settings-filters',
              '--remove-rai-settings-filters',
              '--clear-rai-settings-filters',
              '--enable-floor-setting-enforcement',
          ],
          self.NO_CHANGES_MESSAGE.format(floor_setting=args.full_uri),
      )

    if 'filter_config.rai_settings' in update_mask:
      rai_filters = []
      if floor_setting_updated.filterConfig.raiSettings is not None:
        rai_filters = floor_setting_updated.filterConfig.raiSettings.raiFilters

      if args.IsSpecified('rai_settings_filters'):
        rai_filters = []
        for item in [json.loads(f) for f in args.rai_settings_filters]:
          arg_filter_type = messages.RaiFilter.FilterTypeValueValuesEnum(
              self._GetEnumValue(item['filterType'])
          )
          arg_confidence_level = (
              messages.RaiFilter.ConfidenceLevelValueValuesEnum(
                  self._GetEnumValue(item['confidenceLevel'])
              )
          )
          rai_filters.append(
              messages.RaiFilter(
                  filterType=arg_filter_type,
                  confidenceLevel=arg_confidence_level,
              )
          )
          floor_setting_updated.filterConfig.raiSettings = (
              messages.RaiFilterSettings(raiFilters=rai_filters)
          )
      if args.IsSpecified('add_rai_settings_filters'):
        for item in [json.loads(f) for f in args.add_rai_settings_filters]:
          already_exists = False
          arg_filter_type = messages.RaiFilter.FilterTypeValueValuesEnum(
              self._GetEnumValue(item['filterType'])
          )
          arg_confidence_level = (
              messages.RaiFilter.ConfidenceLevelValueValuesEnum(
                  self._GetEnumValue(item['confidenceLevel'])
              )
          )
          for _, rai_filter in enumerate(rai_filters):
            if arg_filter_type == rai_filter.filterType:
              already_exists = True
              rai_filters.remove(rai_filter)
              rai_filters.append(
                  messages.RaiFilter(
                      filterType=arg_filter_type,
                      confidenceLevel=arg_confidence_level,
                  )
              )
              break
          if not already_exists:
            rai_filters.append(
                messages.RaiFilter(
                    filterType=arg_filter_type,
                    confidenceLevel=arg_confidence_level,
                )
            )
          floor_setting_updated.filterConfig.raiSettings = (
              messages.RaiFilterSettings(raiFilters=rai_filters)
          )

      if args.IsSpecified('remove_rai_settings_filters'):
        for item in json.loads(args.remove_rai_settings_filters):
          arg_filter_type = messages.RaiFilter.FilterTypeValueValuesEnum(
              self._GetEnumValue(item['filterType'])
          )
          arg_confidence_level = (
              messages.RaiFilter.ConfidenceLevelValueValuesEnum(
                  self._GetEnumValue(item['confidenceLevel'])
              )
          )
          for _, rai_filter in enumerate(rai_filters):
            if (
                messages.RaiFilter.FilterTypeValueValuesEnum(arg_filter_type)
                == rai_filter.filterType
                and messages.RaiFilter.ConfidenceLevelValueValuesEnum(
                    arg_confidence_level
                )
                == rai_filter.confidenceLevel
            ):
              rai_filters.remove(rai_filter)
              break
      if args.IsSpecified('clear_rai_settings_filters'):
        floor_setting_updated.filterConfig.raiSettings = None

    if 'filter_config.pi_and_jailbreak_filter_settings' in update_mask:
      if args.IsSpecified('pi_and_jailbreak_filter_settings_enforcement'):
        pi_and_jailbreak_filter_settings_enforcement = self._GetEnumValue(
            args.pi_and_jailbreak_filter_settings_enforcement
        )
        if (
            floor_setting_updated.filterConfig.piAndJailbreakFilterSettings
            is None
        ):
          floor_setting_updated.filterConfig.piAndJailbreakFilterSettings = messages.PiAndJailbreakFilterSettings(
              filterEnforcement=messages.PiAndJailbreakFilterSettings.FilterEnforcementValueValuesEnum(
                  pi_and_jailbreak_filter_settings_enforcement
              )
          )
        else:
          floor_setting_updated.filterConfig.piAndJailbreakFilterSettings.filterEnforcement = messages.PiAndJailbreakFilterSettings.FilterEnforcementValueValuesEnum(
              pi_and_jailbreak_filter_settings_enforcement
          )
      if args.IsSpecified('pi_and_jailbreak_filter_settings_confidence_level'):
        pi_and_jailbreak_filter_settings_confidence_level = self._GetEnumValue(
            args.pi_and_jailbreak_filter_settings_confidence_level
        )
        if (
            floor_setting_updated.filterConfig.piAndJailbreakFilterSettings
            is None
        ):
          floor_setting_updated.filterConfig.piAndJailbreakFilterSettings = messages.PiAndJailbreakFilterSettings(
              confidenceLevel=messages.PiAndJailbreakFilterSettings.ConfidenceLevelValueValuesEnum(
                  pi_and_jailbreak_filter_settings_confidence_level
              )
          )
        else:
          floor_setting_updated.filterConfig.piAndJailbreakFilterSettings.confidenceLevel = messages.PiAndJailbreakFilterSettings.ConfidenceLevelValueValuesEnum(
              pi_and_jailbreak_filter_settings_confidence_level
          )

    if 'filter_config.malicious_uri_filter_settings' in update_mask:
      if args.IsSpecified('malicious_uri_filter_settings_enforcement'):
        if (
            floor_setting_updated.filterConfig.maliciousUriFilterSettings
            is None
        ):
          floor_setting_updated.filterConfig.maliciousUriFilterSettings = messages.MaliciousUriFilterSettings(
              filterEnforcement=messages.MaliciousUriFilterSettings.FilterEnforcementValueValuesEnum(
                  self._GetEnumValue(
                      args.malicious_uri_filter_settings_enforcement
                  )
              )
          )
        else:
          floor_setting_updated.filterConfig.maliciousUriFilterSettings.filterEnforcement = messages.MaliciousUriFilterSettings.FilterEnforcementValueValuesEnum(
              self._GetEnumValue(args.malicious_uri_filter_settings_enforcement)
          )

    if 'filter_config.sdp_settings' in update_mask:
      if args.IsSpecified('basic_config_filter_enforcement'):
        if floor_setting_updated.filterConfig.sdpSettings is None:
          floor_setting_updated.filterConfig.sdpSettings = messages.SdpFilterSettings(
              basicConfig=messages.SdpBasicConfig(
                  filterEnforcement=(
                      messages.SdpBasicConfig.FilterEnforcementValueValuesEnum(
                          self._GetEnumValue(
                              args.basic_config_filter_enforcement
                          )
                      )
                  )
              )
          )
        else:
          floor_setting_updated.filterConfig.sdpSettings.advancedConfig = None
          floor_setting_updated.filterConfig.sdpSettings.basicConfig = messages.SdpBasicConfig(
              filterEnforcement=messages.SdpBasicConfig.FilterEnforcementValueValuesEnum(
                  self._GetEnumValue(args.basic_config_filter_enforcement)
              )
          )
      if args.IsSpecified('advanced_config_inspect_template'):
        if floor_setting_updated.filterConfig.sdpSettings is None:
          floor_setting_updated.filterConfig.sdpSettings = (
              messages.SdpFilterSettings(
                  advancedConfig=messages.SdpAdvancedConfig(
                      inspectTemplate=args.advanced_config_inspect_template
                  )
              )
          )
        else:
          floor_setting_updated.filterConfig.sdpSettings.basicConfig = None
          if (
              floor_setting_updated.filterConfig.sdpSettings.advancedConfig
              is None
          ):
            floor_setting_updated.filterConfig.sdpSettings.advancedConfig = (
                messages.SdpAdvancedConfig(
                    inspectTemplate=args.advanced_config_inspect_template
                )
            )
          else:
            floor_setting_updated.filterConfig.sdpSettings.advancedConfig.inspectTemplate = (
                args.advanced_config_inspect_template
            )
      if args.IsSpecified('advanced_config_deidentify_template'):
        if floor_setting_updated.filterConfig.sdpSettings is None:
          floor_setting_updated.filterConfig.sdpSettings = (
              messages.SdpFilterSettings(
                  advancedConfig=messages.SdpAdvancedConfig(
                      deidentifyTemplate=args.advanced_config_deidentify_template
                  )
              )
          )
        else:
          floor_setting_updated.filterConfig.sdpSettings.basicConfig = None
          if (
              floor_setting_updated.filterConfig.sdpSettings.advancedConfig
              is None
          ):
            floor_setting_updated.filterConfig.sdpSettings.advancedConfig = (
                messages.SdpAdvancedConfig(
                    deidentifyTemplate=args.advanced_config_deidentify_template
                )
            )
          else:
            floor_setting_updated.filterConfig.sdpSettings.advancedConfig.deidentifyTemplate = (
                args.advanced_config_deidentify_template
            )

    if 'enable_floor_setting_enforcement' in update_mask:
      if args.IsSpecified('enable_floor_setting_enforcement'):
        floor_setting_updated.enableFloorSettingEnforcement = (
            args.enable_floor_setting_enforcement.lower() == 'true'
        )
    return api_client.Update(
        name=args.full_uri,
        floor_setting=floor_setting_updated,
        update_mask=update_mask,
    )

  def Run(self, args):
    api_version = model_armor_api.GetApiFromTrack(self.ReleaseTrack())
    full_uri = args.full_uri
    original = model_armor_api.FloorSettings(api_version=api_version).Get(
        full_uri
    )
    return self._RunUpdate(original, args)

