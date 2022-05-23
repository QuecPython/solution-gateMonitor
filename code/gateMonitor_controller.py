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

import quecIot
import net
import sys_bus
from misc import Power

from usr.modules.led import LED
from usr.modules.buzzer import Buzzer
from usr.modules.logging import getLogger
from usr.modules.mpower import LowEnergyManage
from usr.modules.remote import RemotePublish
from usr.modules.common import Singleton
from usr.modules.battery import Battery
from usr.settings import Settings

log = getLogger(__name__)


class Controller(Singleton):
    """Device module control and post data to cloud"""

    def __init__(self):
        self.__red_led = None
        self.__blue_led = None
        self.__buzz = None
        self.__remote_pub = None
        self.__battery = None
        self.__settings = None
        self.__low_energy = None
        self.__lowPowerFlag = True
        self.__data_staging = list()

    def add_module(self, module, led_type=None):
        if isinstance(module, LED):
            if led_type == "red":
                self.__red_led = module
                return True
            elif led_type == "blue":
                self.__blue_led = module
                return True
        if isinstance(module, Buzzer):
            self.__buzz = module
            return True
        if isinstance(module, Battery):
            self.__battery = module
            return True
        if isinstance(module, RemotePublish):
            self.__remote_pub = module
            return True
        if isinstance(module, Settings):
            self.__settings = module
            return True
        if isinstance(module, LowEnergyManage):
            self.__low_energy = module
            return True

    def settings_set(self, key, value):
        if not self.__settings:
            raise TypeError("self.__settings is not registered.")
        set_res = self.__settings.set(key, value)
        log.debug("__settings_set key: %s, val: %s, set_res: %s" % (key, value, set_res))
        return set_res

    def settings_save(self):
        if not self.__settings:
            raise TypeError("self.__settings is not registered.")
        return self.__settings.save()

    def power_restart(self):
        Power.powerRestart()

    def power_down(self):
        Power.powerDown()

    def remote_post_data(self, data):
        if not self.__remote_pub:
            raise TypeError("self.__remote_pub is not registered.")
        log.debug("remote_post_data data: %s" % str(data))
        return self.__remote_pub.post_data(data)

    def remote_ota_check(self):
        if not self.__remote_pub:
            raise TypeError("self.__remote_pub is not registered.")
        return self.__remote_pub.cloud_ota_check()

    def remote_ota_action(self, action, module):
        if not self.__remote_pub:
            raise TypeError("self.__remote_pub is not registered.")
        return self.__remote_pub.cloud_ota_action(action, module)

    def led_on(self, mode=1):
        if not self.__led:
            raise TypeError("self.__led is not registered.")
        if mode: # red
            self.__led = self.__red_led
        else:
            self.__led = self.__blue_led
        return self.__led.on()

    def led_off(self,mode=1):
        if not self.__led:
            raise TypeError("self.__led is not registered.")
        if mode: # red
            self.__led = self.__red_led
        else:
            self.__led = self.__blue_led
        return self.__led.off()

    def led_flicker_on(self, on_period, off_period, count, mode):
        if not self.__led:
            raise TypeError("self.__led is not registered.")
        if mode: # red
            self.__led = self.__red_led
        else:
            self.__led = self.__blue_led
        return self.__led.start_flicker(on_period, off_period, count, mode)

    def led_flicker_off(self, mode):
        if not self.__led:
            raise TypeError("self.__led is not registered.")
        if mode: # red
            self.__led = self.__red_led
        else:
            self.__led = self.__blue_led
        return self.__led.stop_flicker()

    def buzzer_flicker_on(self, on_period, off_period, count):
        if not self.__buzz:
            raise TypeError("self.__buzz is not registered.")
        return self.__buzz.start_flicker(on_period, off_period, count)

    def buzzer_flicker_off(self):
        if not self.__buzz:
            raise TypeError("self.__buzz is not registered.")
        return self.__buzz.stop_flicker()

    def get_device_voltage(self):
        total = self.__battery.get_voltage()
        vbatt = int((total - 1100) / 400 * 100)
        if vbatt < 0:
            vbatt = 1
        if vbatt < 10 and self.__lowPowerFlag:
            self.__lowPowerFlag = False
            sys_bus.publish(1004, {"vbatt": vbatt})
        return vbatt

    def get_net_csq(self):
        return net.csqQueryPoll()

    def get_cloud_sta(self):
        return True if quecIot.getWorkState() == 8 and quecIot.getConnmode() == 1 else False

    def append_repord_data(self, data):
        self.__data_staging.extend(data)

    def rmove_repord_data(self):
        self.__data_staging = []

    def check_report_data(self):
        if self.__data_staging:
            for v in self.__data_staging:
                self.remote_post_data(v)
            return True
        else:
            return False





