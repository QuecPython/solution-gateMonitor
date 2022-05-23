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


class QuecCloudConfig(object):
    """
    object model data format:
    """
    PK = "p111SP"
    PS = "bHBoM01JL1htTEsw"
    DK = ""
    DS = ""
    LIFETIME =  65500
    MODE = 0,  # 0 LWM2M, 1 MQTT
    SERVER = "http://iot-south.quectel.com:5683"

    # Quecthing 物模型事件数据
    # 物模型功能ID
    SWATCH_STATUS = 1  # 门磁开关状态
    SOC = 2  # 电量
    SIGNAL = 3  # 信号强度
    OPEN_ALARM = 6  # 门磁告警
    HEARTBEAT = 7  # 心跳
    LOW_POWER_ALARM = 8  # 低电量告警
    MANUAL_ALARM = 9  # 手动告警
    ALARM_OR_RECOVER = 10  # 低电量告警状态，正常告警or恢复

    # 业务心跳
    HEARTBEAT_DICT = {HEARTBEAT: {SOC: None, SIGNAL: None}}
    # 门磁告警
    OPEN_ALARM_DICT = {OPEN_ALARM: {SWATCH_STATUS: None, SOC: None, SIGNAL: None}}
    # 低电量告警
    LOW_POWER_ALARM_DICT = {LOW_POWER_ALARM: {SOC: None, SIGNAL: None, ALARM_OR_RECOVER: True}}
    # 手动告警
    MANUAL_ALARM_DICT = {MANUAL_ALARM: {SOC: None, SIGNAL: None}}
