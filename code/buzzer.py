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


import _thread
import osTimer
from machine import Pin
from usr.logging import getLogger

log = getLogger(__name__)


class Buzzer(object):
    def __init__(self, GPIOn, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0):
        self.__buzz = Pin(GPIOn, direction, pullMode, level)
        self.__buzz_timer = osTimer()
        self.__buzz_lock = _thread.allocate_lock()

    def on(self):
        self.__buzz.write(1)

    def off(self):
        self.__buzz.write(0)

    def switch(self):
        pass

