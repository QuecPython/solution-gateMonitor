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

from misc import Power
from usr.modules.common import Singleton
from usr.gateMonitor_controller import Controller
from usr.gateMonitor_devicecheck import DeviceCheck


class Collector(Singleton):
    """Device data and commands collector"""
    def __init__(self):
        self.__controller = None
        self.__devicecheck = None
        self.__bootReason = Power.powerOnReason()

    def add_module(self, module):
        """add modules for collecting data"""
        if isinstance(module, Controller):
            self.__controller = module
            return True
        elif isinstance(module, DeviceCheck):
            self.__devicecheck = module
            return True

    def device_status_get(self):
        """Get device status from DeviceCheck module"""
        if not self.__devicecheck:
            raise TypeError("self.__devicecheck is not registered.")
        if not self.__controller:
            raise TypeError("self.__controller is not registered.")

        self.device_power_on()
        net_status = self.__devicecheck.wait_net_state()
        if net_status:
            self.__controller.led_flicker_off(0)
            self.__controller.buzzer_flicker_on(1000, 100, 1)
        else:
            self.__controller.led_on(1)
            self.__controller.buzzer_flicker_on(600, 400, 2)
        return net_status

    def device_power_on(self):
        if (self.__bootReason != 4) and (self.__bootReason != 8):
            self.__controller.buzzer_flicker_on(700, 300, 1)
            self.__controller.led_flicker_on(500, 500, 60, 0)



