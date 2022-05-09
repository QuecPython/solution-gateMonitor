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
from usr.logging import getLogger
from usr.settings import ConfigModule


log = getLogger(__name__)

class QuecThing(object):
    '''
    QuecIot DMP
    '''
    def __init__(self):
        self.__quecIotParamDict = ConfigModule.quecIotConnectParam()

    def quecIotInit(self):
        '''
        初始化quecIot连接属性，配置产品PK、PS
        '''
        pk = self.__quecIotParamDict.get("PK")
        ps = self.__quecIotParamDict.get("PS")
        lifetime = self.__quecIotParamDict.get("LIFETIME")
        mode = self.__quecIotParamDict.get("MODE")
        server = self.__quecIotParamDict.get("SERVER")
        self.setCallback()
        quecIot.setProductinfo(pk, ps)
        quecIot.setServer(mode, server)
        quecIot.setLifetime(lifetime)

    def setCallback(self):
        # 设备事件回调函数
        quecIot.setEventCB(self.__callback)

    def connect(self):
        '''启动云平台连接'''
        connect_sta = quecIot.setConnmode(1)
        return connect_sta

    def disconnect(self):
        disconnect_sta  = quecIot.setConnmode(0)
        return disconnect_sta

    def phymodelReport(self, data, mode=0):
        '''
        发送物模型数据
        mode: 消息发送模式,int类型,默认为2
            协议为 MQTT：
            0 QoS=0，仅发送一次。
            1 QoS=1，最少发送一次。
            2 QoS=2，最多发送一次。
            若协议为 LwM2M：
            0 发送 NON 消息。
            1 发送 NON 消息并携带 RELEASE 标记。
            2 发送 CON 消息。
            3 发送 CON 消息并携带 RELEASE_AFTER_REPLY 标记。
        data: dict类型，待上报的数据
        '''
        send_sta = quecIot.phymodelReport(mode, data)
        return send_sta

    def phymodelAck(self, pkgid, data, mode=2):
        '''
        应答云平台物模型数据
        pkgid：请求包ID,int类型
        mode: 消息发送模式,int类型, 默认为2
            协议为 MQTT：
            0 QoS=0，仅发送一次。
            1 QoS=1，最少发送一次。
            2 QoS=2，最多发送一次。
            若协议为 LwM2M：
            0 发送 NON 消息。
            1 发送 NON 消息并携带 RELEASE 标记。
            2 发送 CON 消息。
            3 发送 CON 消息并携带 RELEASE_AFTER_REPLY 标记。
        data: 待上报的数据,dict类型
        '''
        send_sta = quecIot.phymodelAck(mode, pkgid, data)
        return send_sta

    def passTransSend(self, data, mode=2):
        '''
        发送透传数据
        mode: 消息发送模式,int类型,默认为2
            协议为 MQTT：
            0 QoS=0，仅发送一次。
            1 QoS=1，最少发送一次。
            2 QoS=2，最多发送一次。
            若协议为 LwM2M：
            0 发送 NON 消息。
            1 发送 NON 消息并携带 RELEASE 标记。
            2 发送 CON 消息。
            3 发送 CON 消息并携带 RELEASE_AFTER_REPLY 标记。
        data: bytes类型，待上报的数据
        '''
        send_sta = quecIot.passTransSend(mode, data)
        return send_sta

    def otaRequest(self):
        # 触发升级计划
        quecIot.otaRequest(0)

    def otaAction(self, mode=1):
        # 有升级计划， mode=1,确认升级； mode=0,拒绝升级，默认为1
        quecIot.otaAction(mode)

    def __callback(self, data):
        '''
        云端事件回调函数
        data: list
        '''
        log.info("event: %s" % str(data))
