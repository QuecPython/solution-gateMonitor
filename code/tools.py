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

class DataFormat(object):

    @classmethod
    def reportData(cls, event, msg=None):
        '''
        data : dict类型数据
        return : 输出待上报的数据
        '''
        if event == OPEN_ALARM:
            alarm_dict = {SWATCH_STATUS: msg, SOC: cls.Voltage, SIGNAL: cls.CSQ}
            data = OPEN_ALARM_DICT.get(OPEN_ALARM).update(alarm_dict)
        elif event == HEARTBEAT:
            alarm_dict = {SOC: cls.Voltage, SIGNAL: cls.CSQ}
            data = HEARTBEAT_DICT.get(HEARTBEAT).update(alarm_dict)
        elif event == LOW_POWER_ALARM:
            alarm_dict = {SOC: cls.Voltage, SIGNAL: cls.CSQ, ALARM_OR_RECOVER: msg}
            data = LOW_POWER_ALARM_DICT.get(LOW_POWER_ALARM).update(alarm_dict)
        elif event == MANUAL_ALARM:
            alarm_dict = {SOC: cls.Voltage, SIGNAL: cls.CSQ}
            data = MANUAL_ALARM_DICT.get(MANUAL_ALARM).update(alarm_dict)
        else:
            raise ValueError("event ID does not exist")
        return data