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

from misc import ADC
from usr.logging import getLogger
from usr.common import Singleton

log = getLogger(__name__)

class Battery(Singleton):
    '''
    ADC init
    '''
    def __init__(self):
        self.__adc = ADC
        self.__adc.open()

    def conversionVoltage(self):
        adc_list = [self.__adc.read(ADC.ADC0) for i in range(20)]
        # 去掉一个最高值和最低值，在求取平均值
        adc_list.remove(min(adc_list))
        adc_list.remove(max(adc_list))
        voltage = int(((sum(adc_list) / 18 - 1100) / 400) * 100)
        return voltage

    @classmethod
    def getVoltage(cls):
        voltage = cls().conversionVoltage()
        if voltage < 0:
            voltage = 1
        return_voltage = 100 if voltage > 100 else voltage
        return return_voltage


