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
import utime
from machine import Pin
from log import getLogger

log = getLogger(__name__)


class Buzzer(object):
    """This class is for control Buzzer"""
    def __init__(self, GPIOn, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0):
        self.__buzz = Pin(GPIOn, direction, pullMode, level)
        self.__buzz_timer = osTimer()
        self.thread_id = None

    def on(self):
        self.__buzz.write(1)

    def off(self):
        self.__buzz.write(0)

    def __buzz_timer_cb(self, count, on_period, off_period):
        """buzz flicker timer."""
        for i in range(0, count):
            self.on()
            utime.sleep_ms(on_period)
            self.off()
            utime.sleep_ms(off_period)
        self.thread_id = None

    def start_flicker(self, on_period, off_period, count):
        """Start buzz period"""
        if self.thread_id:
            log.info("start_flicker is thread_id Y")
            return False
        self.thread_id = _thread.start_new_thread(self.__buzz_timer_cb, (count, on_period, off_period))
        return True

    def stop_flicker(self):
        """Stop buzz period"""
        try:
            if self.thread_id:
                _thread.stop_thread(self.thread_id)
        except:
            print("stop buzz error")

class LED(object):
    """This class is for control LED"""

    def __init__(self, GPIOn, direction=Pin.OUT, pullMode=Pin.PULL_DISABLE, level=0):
        """LED object init"""
        self.__led = Pin(GPIOn, direction, pullMode, level)
        self.thread_id = None
        self.__led_timer = osTimer()

    def on(self):
        """Set led on"""
        self.__led.write(1)

    def off(self):
        """Set led off"""
        self.__led.write(0)

    def __led_timer_cb(self, count, on_period, off_period):
        """LED flicker timer."""
        for i in range(0, count):
            self.on()
            utime.sleep_ms(on_period)
            self.off()
            utime.sleep_ms(off_period)
        self.off()
        self.thread_id = None

    def start_flicker(self, on_period, off_period, count):
        """Start led flicker"""
        if self.thread_id:
            return False
        self.thread_id = _thread.start_new_thread(self.__led_timer_cb, (count, on_period, off_period))
        return True

    def stop_flicker(self):
        """Stop LED flicker"""
        try:
            if self.thread_id:
                _thread.stop_thread(self.thread_id)
            self.off()
        except:
            print("stop buzz error")