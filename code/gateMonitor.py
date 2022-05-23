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
import _thread
import utime
from misc import Power
from queue import Queue
from machine import Pin
from machine import ExtInt

from usr.modules.common import Singleton
from usr.modules.logging import getLogger
from usr.gateMonitor_controller import Controller
from usr.settings import settings

log = getLogger(__name__)


class GateMonitor(Singleton):
    def __init__(self, config):
        self.__controller = None
        self.__extint = None
        self.__config = config
        self.__bootReason = Power.powerOnReason()

    def add_module(self, module):
        """add modules for collecting data"""
        if isinstance(module, Controller):
            self.__controller = module
            return True
        if isinstance(module, InterruptEvent):
            self.__extint = module
            return True

    def deviceAlarm(self, topic, params):
        '''
        门磁告警
        '''
        door_sta = params.get("door_status")
        mode = params.get("mode")
        if door_sta: # door sta open
            self.__controller.led_flicker(1000, 300, 5, 1)
            self.__controller.buzzer_flicker(1000, 300, 5)
        else:
            self.__controller.led_flicker(1000, 300, 1, 0)
            self.__controller.buzzer_flicker(1000, 300, 1)
        # 根据物模型定义的告警事件属性值进行组包
        csq = self.__controller.get_net_csq()
        voltage = self.__controller.get_device_voltage()
        if mode == 1: # chose and open
            report_data = [{6: {1: False, 2: voltage, 3: csq}}, {6: {1: True, 2: voltage, 3: csq}}]
        elif mode == 2: # open and close
            report_data = [{6: {1: True, 2: voltage, 3: csq}}, {6: {1: False, 2: voltage, 3: csq}}]
        else:  # close or open
            report_data = [{6: {1: door_sta, 2: voltage, 3: csq}}]
        if self.__controller.get_cloud_sta():
            for v in report_data:
                self.__controller.remote_post_data(v)
        else:
            self.__controller.append_repord_data(report_data)

    def periodicHeartbeat(self, topic, params):
        '''
        rtc 周期心跳
        '''
        # 根据物模型定义的告警事件属性值进行组包
        csq = self.__controller.get_net_csq()
        voltage = self.__controller.get_device_voltage()
        report_data = {7: {2: voltage, 3: csq}}
        send_sta = self.__controller.remote_post_data(report_data)
        return send_sta

    def manualAlarm(self, topic, params):
        '''
        按键 手动告警
        '''
        self.__controller.led_flicker(3000, 300, 1, 1)
        self.__controller.buzzer_flicker(600, 400, 3)
        # 根据物模型定义的告警事件属性值进行组包
        csq = self.__controller.get_net_csq()
        voltage = self.__controller.get_device_voltage()
        report_data = [{9: {2: voltage, 3: csq}}]
        if self.__controller.get_cloud_sta():
            for v in report_data:
                self.__controller.remote_post_data(v)
        else:
            self.__controller.append_repord_data(report_data)

    def lowPowerAlarm(self, topic, params):
        '''
        低电量告警
        '''
        # 根据物模型定义的告警事件属性值进行组包
        csq = self.__controller.get_net_csq()
        voltage = params.get("params")
        report_data = {8: {2: voltage, 3: csq, 10: True}}
        send_sta = self.__controller.remote_post_data(report_data)
        return send_sta

    def deviceWakeUp(self):
        if self.__bootReason == 8:
            if self.__extint.get_key_gpio_level():
                self.__extint.eventQueue.put([7, 5])
            else:
                self.__extint.eventQueue.put([6, 5])

    def powerOnManage(self, cloud_sta):
        if cloud_sta:
            sys_bus.publish(1001, {"cmd": 1001})
            self.__controller.check_report_data()
            self.__controller.remote_ota_check()

    def makeFunctions(self):
        '''
        订阅任务到sys_bus
        '''
        self.__taskCode = {
            1001: self.periodicHeartbeat,
            1002: self.deviceAlarm,
            1003: self.manualAlarm,
            1004: self.lowPowerAlarm,
        }
        for k, v in self.__msgCode.items():
            sys_bus.subscribe(k, v)


class InterruptEvent(object):
    def __init__(self, config):
        self.__config = config
        self.eventQueue = Queue(20)
        self.__magnet_ext = ExtInt(ExtInt.GPIO6, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_DISABLE, self.__magnetCallback)
        self.__keys_ext = ExtInt(ExtInt.GPIO7, ExtInt.IRQ_FALLING, ExtInt.PULL_DISABLE, self.__keyCallback)
        self.__magnet_ext.enable()
        self.__keys_ext.enable()
        self.__magnet_gpio = Pin(Pin.GPIO6, Pin.IN, Pin.PULL_DISABLE, 1)
        self.__key_gpio = Pin(Pin.GPIO7, Pin.IN, Pin.PULL_DISABLE, 1)

    def __magnetCallback(self, args):
        now_level = args[1]
        utime.sleep_ms(25)
        if (now_level == self.__magnet_gpio.read()) and self.__magnet_flag:
            self.__magnet_flag = False
            self.eventQueue.put(args)
        else:
            pass

    def __keyCallback(self, args):
        now_level = args[1]
        utime.sleep_ms(25)
        if (now_level == self.__key_gpio.read()) and self.__keys_flag:
            self.__keys_flag = False
            self.eventQueue.put(args)
        else:
            pass

    def get_key_gpio_level(self):
        return self.__key_gpio.read()

    def runTask(self):
        _thread.start_new_thread(self.interruptManage, ())

    def interruptManage(self):
        while True:
            msg = self.eventQueue.get()
            try:
                if msg[0] == 7:
                    sys_bus.publish(1003, {"cmd": 1003})
                    self.__keys_flag = True
                else:
                    level = self.__magnet_gpio.read()
                    doorSta = settings.get("device_cfg").get("door_status")
                    if doorSta and not level: # 上次记录门磁状态为开 本次唤醒读取状态为关 判断为关门动作，执行关门恢复告警
                        doorSta = False
                        action_mode = 0
                    elif not doorSta and level: # 上次记录门磁状态为关 本次唤醒读取状态为开 判断为开门动作，执行开门告警
                        doorSta = True
                        action_mode = 0
                    elif doorSta and level: # 上次记录门磁状态为开 本次唤醒读取状态也为开 判断为一关一开的动作，执行开门告警
                        doorSta = True
                        action_mode = 1
                    elif not doorSta and not level: # 上次记录门磁状态为关 本次唤醒读取状态为关 判断为一开一关动作，执行开门告警
                        doorSta = False
                        action_mode = 2
                    else:
                        doorSta = True
                        action_mode = 0
                    sys_bus.publish(1002, {"door_status": doorSta, "mode": action_mode})
                    self.__magnet_flag = True
                    settings.set("door_state", 1 if doorSta else 0)
                    settings.save()
            except Exception as e:
                self.__magnet_flag = True
                self.__keys_flag = True






