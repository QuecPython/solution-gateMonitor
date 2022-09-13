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

import net
import checkNet
import sys_bus
import pm
from misc import Power
from usr.modules.peripherals import Buzzer, LED
from log import getLogger
from usr.modules.mpower import LowEnergyManage
from usr.modules.remote import RemotePublish
from usr.modules.common import Singleton
from usr.modules.battery import Battery
from usr.settings import Settings, PROJECT_NAME, PROJECT_VERSION, settings

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
        log.info("DEBUG:remote_post_data data: %s" % str(data))
        return self.__remote_pub.post_data(data)

    def remote_ota_check(self):
        if not self.__remote_pub:
            raise TypeError("self.__remote_pub is not registered.")
        return self.__remote_pub.cloud_ota_check()

    def remote_ota_action(self, action, module):
        if not self.__remote_pub:
            raise TypeError("self.__remote_pub is not registered.")
        return self.__remote_pub.cloud_ota_action(action, module)

    def low_energy_init(self):
        if not self.__low_energy:
            raise TypeError("self.__low_energy is not registered.")
        return self.__low_energy.low_energy_init()

    def low_energy_start(self):
        if not self.__low_energy:
            raise TypeError("self.__low_energy is not registered.")
        return self.__low_energy.start()

    def led_on(self, mode=1):
        if not self.__red_led and self.__blue_led:
            raise TypeError("self.__led is not registered.")
        if mode:  # red
            self.__led = self.__red_led
        else:
            self.__led = self.__blue_led
        return self.__led.on()

    def led_off(self, mode=1):
        if not self.__red_led and self.__blue_led:
            raise TypeError("self.__led is not registered.")
        if mode:  # red
            self.__led = self.__red_led
        else:
            self.__led = self.__blue_led
        return self.__led.off()

    def led_flicker_on(self, on_period, off_period, count, mode):
        if mode:  # red
            self.__led = self.__red_led
        else:
            self.__led = self.__blue_led
        return self.__led.start_flicker(on_period, off_period, count)

    def led_flicker_off(self, mode):
        if mode:  # red
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
        device_voltage_num = int((self.__battery.get_voltage() - 1100) / 400 * 100)
        if device_voltage_num < 0:
            device_voltage_num = 1
        if device_voltage_num < 10 and self.__lowPowerFlag:
            self.__lowPowerFlag = False
            sys_bus.publish(1004, {"vbatt": device_voltage_num})
        return device_voltage_num

    def get_net_csq(self):
        return net.csqQueryPoll()

    def get_cloud_sta(self):
        return self.__remote_pub.conn_state()

    def append_repord_data(self, data):
        self.__data_staging.extend(data)

    def rmove_repord_data(self):
        self.__data_staging = []

    def check_report_data(self):
        log.info("report_data is %s " % self.__data_staging)
        if self.__data_staging:
            for v in self.__data_staging:
                self.remote_post_data(v)
            return True
        else:
            return False


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
        stagecode, subcode = checknet.wait_network_connected(timeout)
        log.info("DeviceCheck.net stagecode: %s, subcode: %s" % (stagecode, subcode))
        return True if (stagecode == 3 and subcode == 1) else False


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
        return net_status

    def device_connect_cloud(self, cloud, net_status):
        if net_status:
            cloud_status = cloud.init(enforce=True)
            if cloud_status:
                if (self.__bootReason == 1) or (self.__bootReason == 2):
                    pm.set_psm_time(1, 24, 0, 1)
                    self.__controller.led_flicker_off(0)
                    self.__controller.buzzer_flicker_on(2000, 100, 1)
                return True
        self.__controller.led_on(1)
        self.__controller.buzzer_flicker_on(600, 400, 2)
        return False

    def device_power_on(self):
        if self.__bootReason == 1 or self.__bootReason == 2:
            self.__controller.buzzer_flicker_on(700, 300, 1)
            self.__controller.led_flicker_on(500, 500, 60, 0)
