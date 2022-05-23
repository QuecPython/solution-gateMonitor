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

import sys_bus
from machine import Pin
from misc import ADC

from usr.modules.logging import getLogger
from usr.modules.history import History
from usr.modules.battery import Battery
from usr.modules.led import LED
from usr.modules.buzzer import Buzzer
from usr.modules.remote import RemotePublish
from usr.modules.mpower import LowEnergyManage
from usr.modules.quecthing import QuecThing, QuecObjectModel
from usr.gateMonitor_controller import Controller
from usr.gateMonitor_collector import Collector
from usr.gateMonitor_devicecheck import DeviceCheck
from usr.gateMonitor import GateMonitor, InterruptEvent
from usr.settings import PROJECT_NAME, PROJECT_VERSION, DEVICE_FIRMWARE_NAME,\
    DEVICE_FIRMWARE_VERSION, settings, SYSConfig

log = getLogger(__name__)

def main():
    log.info("PROJECT_NAME: %s, PROJECT_VERSION: %s" % (PROJECT_NAME, PROJECT_VERSION))
    log.info("DEVICE_FIRMWARE_NAME: %s, DEVICE_FIRMWARE_VERSION: %s" % (DEVICE_FIRMWARE_NAME, DEVICE_FIRMWARE_VERSION))

    current_settings = settings.get()

    history_obj = History()
    battery_obj = Battery((ADC.ADC0, 20, 1))
    red_led_obj = LED(Pin.GPIO4)
    blue_led_obj = LED(Pin.GPIO3)
    buzzer_obj = Buzzer(Pin.GPIO2)
    low_energy_obj = LowEnergyManage()
    devicecheck_obj = DeviceCheck()
    extint_obj = InterruptEvent(current_settings)
    gate_monitor_obj = GateMonitor()
    gate_monitor_obj.makeFunctions()

    cloud_init_params = current_settings["cloud"]
    if current_settings["sys"]["cloud"] & SYSConfig._cloud.quecIot:
        cloud = QuecThing(
            cloud_init_params["PK"],
            cloud_init_params["PS"],
            cloud_init_params["DK"],
            cloud_init_params["DS"],
            cloud_init_params["SERVER"],
            life_time = cloud_init_params["LIFETIME"],
            mcu_name=PROJECT_NAME,
            mcu_version=PROJECT_VERSION,
            mode = cloud_init_params["MODE"],
        )
        # Cloud object model init
        cloud_om = QuecObjectModel()
        cloud.set_object_model(cloud_om)

    # RemotePublish initialization
    remote_pub = RemotePublish()
    # Add History to RemotePublish for recording failure data
    remote_pub.addObserver(history_obj)
    # Add Cloud to RemotePublish for publishing data to cloud
    remote_pub.add_cloud(cloud)

    # Controller initialization
    controller = Controller()
    # Add RemotePublish to Controller for publishing data to cloud
    controller.add_module(remote_pub)
    # Add Settings to Controller for changing settings.
    controller.add_module(settings)
    # Add LowEnergyManage to Controller for controlling low energy.
    controller.add_module(low_energy_obj)
    # Add led to Controller
    controller.add_module(red_led_obj, led_type="red")
    controller.add_module(blue_led_obj, led_type="blue")
    # Add Buzzer to Controller
    controller.add_module(buzzer_obj)
    # Add Battery to Controller
    controller.add_module(battery_obj)

    # Collector initialization
    collector = Collector()
    collector.add_module(devicecheck_obj)
    collector.add_module(controller)

    gate_monitor_obj.add_module(extint_obj)
    gate_monitor_obj.add_module(collector)

    extint_obj.runTask()
    gate_monitor_obj.deviceWakeUp()
    net_status = collector.device_status_get()
    if net_status:
        # Business start
        # Cloud start
        cloud_status = cloud.init()
        gate_monitor_obj.powerOnManage(cloud_status)
    rtc_wakeup_period = current_settings["user_cfg"]["rtc_wakeup_period"]
    low_energy_obj.set_period(rtc_wakeup_period)
    low_energy_obj.set_low_energy_method(collector.__init_low_energy_method(rtc_wakeup_period))
    low_energy_obj.addObserver(collector)
    # Low energy init
    controller.low_energy_init()
    # Low energy start
    controller.low_energy_start()



if __name__ == '__main__':
    main()