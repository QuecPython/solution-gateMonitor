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

from usr.led import Buzzer
from usr.led import Led
from usr.quecthing import QuecThing
from usr.common import Singleton
from usr.logging import getLogger
from usr.common import DataFormat
from usr.settings import OPEN_ALARM, HEARTBEAT, LOW_POWER_ALARM, MANUAL_ALARM

log = getLogger(__name__)


class GateMonitor(Singleton):
    def __init__(self, *args, **kwargs):

        self.led = Led()
        self.buzz = Buzzer()
        self.quecIot = QuecThing()

    def DeviceAlarm(self, topic, params):
        '''
        门磁告警
        '''
        door_sta = params.get("door_status")
        # 根据物模型定义的告警事件属性值进行组包
        report_data = DataFormat.reportData(OPEN_ALARM, msg=door_sta)
        send_sta = self.quecIot.phymodelReport(report_data, mode=2)
        return send_sta

    def periodicHeartbeat(self, topic, params):
        '''
        rtc 周期心跳
        '''
        # 根据物模型定义的告警事件属性值进行组包
        report_data = DataFormat.reportData(HEARTBEAT)
        send_sta = self.quecIot.phymodelReport(report_data, mode=2)
        return send_sta

    def manualAlarm(self, topic, params):
        '''
        按键 手动告警
        '''
        # 根据物模型定义的告警事件属性值进行组包
        report_data = DataFormat.reportData(MANUAL_ALARM)
        send_sta = self.quecIot.phymodelReport(report_data, mode=2)
        return send_sta

    def lowPowerAlarm(self, topic, params):
        '''
        低电量告警
        '''
        # 根据物模型定义的告警事件属性值进行组包
        report_data = DataFormat.reportData(LOW_POWER_ALARM, msg=True)
        send_sta = self.quecIot.phymodelReport(report_data, mode=2)
        return send_sta

    def makeFunctions(self):
        '''
        订阅任务到sys_bus
        '''
        self.__taskCode = {
            1001: self.periodicHeartbeat,
            1002: self.DeviceAlarm,
            1003: self.manualAlarm,
        }
        for k, v in self.__msgCode.items():
            sys_bus.subscribe(k, v)



