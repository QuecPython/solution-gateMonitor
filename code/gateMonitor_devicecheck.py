# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import checkNet

from usr.gateMonitor_controller import Controller
from usr.modules.logging import getLogger
from usr.settings import PROJECT_NAME, PROJECT_VERSION, settings

log = getLogger(__name__)


class DeviceCheck(object):

    def __init__(self):
        self.__controller = None

    def add_module(self, module):
        """add modules for collecting data"""
        if isinstance(module, Controller):
            self.__controller = module
            return True

    def wait_net_state(self):
        current_settings = settings.get()
        checknet = checkNet.CheckNetwork(PROJECT_NAME, PROJECT_VERSION)
        timeout = current_settings.get("sys", {}).get("checknet_timeout", 60)
        self.__controller.led_flicker_on(600, 400, timeout * 1000, 0)
        stagecode, subcode = checknet.wait_network_connected(timeout)
        log.debug("DeviceCheck.net stagecode: %s, subcode: %s" % (stagecode, subcode))
        if stagecode == 3 and subcode == 1:
            self.__controller.led_flicker_off(0)
            self.__controller.buzzer_flicker_on(1500, 100, 1)
        else:
            self.__controller.led_on()
            self.__controller.buzzer_flicker_on(600, 400, 2)
        return stagecode, subcode

    def device_power_on(self):
        self.__controller.buzzer_flicker_on(700, 300, 1)
