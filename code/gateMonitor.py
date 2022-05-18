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
from machine import Pin
from machine import ExtInt
from queue import Queue

from usr.modules.common import Singleton
from usr.modules.logging import getLogger
from usr.gateMonitor_controller import Controller

log = getLogger(__name__)


class GateMonitor(Singleton):
    def __init__(self, *args, **kwargs):
        self.__controller = None

    def add_module(self, module):
        """add modules for collecting data"""
        if isinstance(module, Controller):
            self.__controller = module
            return True

    def deviceAlarm(self, topic, params):
        '''
        门磁告警
        '''
        door_sta = params.get("door_status")
        if door_sta: # door sta open
            self.__controller.led_flicker(1000, 300, 5, 1)
            self.__controller.buzzer_flicker(1000, 300, 5)
        else:
            self.__controller.led_flicker(1000, 300, 1, 0)
            self.__controller.buzzer_flicker(1000, 300, 1)
        # 根据物模型定义的告警事件属性值进行组包
        report_data = {}
        send_sta = self.__controller.remote_post_data(report_data)
        return send_sta

    def periodicHeartbeat(self, topic, params):
        '''
        rtc 周期心跳
        '''
        # 根据物模型定义的告警事件属性值进行组包
        report_data = {}
        send_sta = self.__controller.remote_post_data(report_data)
        return send_sta

    def manualAlarm(self, topic, params):
        '''
        按键 手动告警
        '''
        self.__controller.led_flicker(3000, 300, 1, 1)
        self.__controller.buzzer_flicker(600, 400, 3)
        # 根据物模型定义的告警事件属性值进行组包
        report_data = {}
        send_sta = self.__controller.remote_post_data(report_data)
        return send_sta

    def lowPowerAlarm(self, topic, params):
        '''
        低电量告警
        '''
        # 根据物模型定义的告警事件属性值进行组包
        report_data = {}
        send_sta = self.__controller.remote_post_data(report_data)
        return send_sta

    def makeFunctions(self):
        '''
        订阅任务到sys_bus
        '''
        self.__taskCode = {
            1001: self.periodicHeartbeat,
            1002: self.deviceAlarm,
            1003: self.manualAlarm,
        }
        for k, v in self.__msgCode.items():
            sys_bus.subscribe(k, v)


class InterruptEvent(object):
    def __init__(self):
        self.__eventQueue = Queue(20)
        self.__magnet_ext = ExtInt(ExtInt.GPIO6, ExtInt.IRQ_RISING_FALLING, ExtInt.PULL_DISABLE, self.__magnetCallback)
        self.__keys_ext = ExtInt(ExtInt.GPIO7, ExtInt.IRQ_FALLING, ExtInt.PULL_DISABLE, self.__keyCallback)
        self.__magnet_ext.enable()
        self.__keys_ext.enable()
        self.__magnet_gpio = Pin(Pin.GPIO6, Pin.IN, Pin.PULL_DISABLE, 1)
        self.key_gpio = Pin(Pin.GPIO7, Pin.IN, Pin.PULL_DISABLE, 1)

    def __magnetCallback(self, args):
        if self.__magnet_flag:
            self.__magnet_flag = False
            self.__eventQueue.put(args)

    def __keyCallback(self, args):
        if self.__keys_flag:
            self.__keys_flag = False
            self.__eventQueue.put(args)

    def runTask(self):
        _thread.start_new_thread(self.interruptManage, ())

    def interruptManage(self):
        while True:
            msg = self.__eventQueue.get()
            try:
                if msg[0] == 7:
                    sys_bus.publish(1003, {"cmd": 1003})
                    self.__keys_flag = True
                else:
                    level = self.__magnet_gpio.read()
                    doorSta = PsmOperation.readFile("deviceConfig.json").get("door_status")
                    if doorSta and not level: # 上次记录门磁状态为开 本次唤醒读取状态为关 判断为关门动作，执行关门恢复告警
                        sys_bus.publish(1002, {"door_status": False})
                    elif not doorSta and level: # 上次记录门磁状态为关 本次唤醒读取状态为开 判断为开门动作，执行开门告警
                        sys_bus.publish(1002, {"door_status": True})
                    self.__magnet_flag = True
            except Exception as e:
                self.__magnet_flag = True
                self.__keys_flag = True



