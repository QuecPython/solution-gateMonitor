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

import pm
import utime
import _thread
import osTimer

from queue import Queue

from usr.modules.common import Observable
from log import getLogger
from machine import RTC


log = getLogger(__name__)
LOW_ENERGY_METHOD = ("NULL", "PM", "PSM", "POWERDOWN")

class LowEnergyManage(Observable):
    """This class is managing low energy wake up"""

    def __init__(self):
        super().__init__()

        self.__timer = None

        self.__period = 60
        self.__low_energy_method = "PM"
        self.__thread_id = None

        self.__lpm_fd = None
        self.__pm_lock_name = "low_energy_pm_lock"
        self.__low_energy_queue = Queue(maxsize=8)

    def __timer_callback(self, args):
        """This callback is for interrupting sleep"""
        self.__low_energy_queue.put(self.__low_energy_method)

    def __low_energy_work(self, lowenergy_tag):
        """This function is for notify Observers after interrupting sleep"""
        while True:
            data = self.__low_energy_queue.get()
            log.debug("__low_energy_work data: %s, lowenergy_tag: %s" % (data, lowenergy_tag))
            if data:
                if lowenergy_tag:
                    if self.__lpm_fd is None:
                        self.__lpm_fd = pm.create_wakelock(self.__pm_lock_name, len(self.__pm_lock_name))
                        pm.autosleep(1)
                    wlk_res = pm.wakelock_lock(self.__lpm_fd)
                    log.debug("pm.wakelock_lock %s." % ("Success" if wlk_res == 0 else "Falied"))

                self.notifyObservers(self, *(data,))

                if lowenergy_tag:
                    wulk_res = pm.wakelock_unlock(self.__lpm_fd)
                    log.debug("pm.wakelock_unlock %s." % ("Success" if wulk_res == 0 else "Falied"))

    def __timer_init(self):
        """Use RTC or osTimer for timer"""
        if RTC is not None:
            self.__timer = RTC()
        else:
            if self.__low_energy_method in ("PSM", "POWERDOWN"):
                raise TypeError("osTimer not support %s!" % self.__low_energy_method)
            self.__timer = osTimer()

    def __rtc_enable(self, enable):
        """Enable or disable RTC"""
        print(self.__timer)
        enable_alarm_res = self.__timer.enable_alarm(enable)
        return True if enable_alarm_res == 0 else False

    def __rtc_start(self):
        """Start low energy sleep by RTC"""
        self.__timer.register_callback(self.__timer_callback)
        atime = utime.localtime(utime.mktime(utime.localtime()) + self.__period)
        alarm_time = [atime[0], atime[1], atime[2], atime[6], atime[3], atime[4], atime[5], 0]
        if self.__timer.set_alarm(alarm_time) == 0:
            return self.__rtc_enable(1)
        return False

    def __rtc_stop(self):
        """Stop low energy sleep by RTC"""
        return self.__rtc_enable(0)

    def __timer_start(self):
        """Start low energy sleep by osTimer"""
        res = self.__timer.start(self.__period * 1000, 0, self.__timer_callback)
        return True if res == 0 else False

    def __timer_stop(self):
        """Stop low energy sleep by osTimer"""
        res = self.__timer.stop()
        log.debug("__timer_stop res: %s" % res)
        return True if res == 0 else False

    def get_period(self):
        """Get low energy interrupting sleep period"""
        return self.__period

    def set_period(self, seconds=0):
        """Set low energy interrupting sleep period"""
        if isinstance(seconds, int) and seconds > 0:
            self.__period = seconds
            return True
        return False

    def get_low_energy_method(self):
        """Get low energy method"""
        return self.__low_energy_method

    def set_low_energy_method(self, method):
        """Set low energy method"""
        if method in LOW_ENERGY_METHOD:
            if RTC is None and method in ("PSM", "POWERDOWN"):
                return False
            self.__low_energy_method = method
            return True
        return False

    def get_lpm_fd(self):
        """Get PM(wake lock) lock id"""
        return self.__lpm_fd

    def low_energy_init(self):
        """Init low energy"""
        # try:
        if self.__thread_id is not None:
            _thread.stop_thread(self.__thread_id)
        if self.__lpm_fd is not None:
            pm.delete_wakelock(self.__lpm_fd)
            self.__lpm_fd = None

        if self.__low_energy_method in ("PM", "PSM"):
            # self.__thread_id = _thread.start_new_thread(self.__low_energy_work, (True,))
            # self.__lpm_fd = pm.create_wakelock(self.__pm_lock_name, len(self.__pm_lock_name))
            pm.autosleep(1)
        elif self.__low_energy_method in ("NULL", "POWERDOWN"):
            self.__thread_id = _thread.start_new_thread(self.__low_energy_work, (False,))

        self.__timer_init()
        return True

    def start(self):
        """Start low energy sleep"""
        if RTC is not None:
            return self.__rtc_start()
        else:
            return self.__timer_start()

    def stop(self):
        """Stop low energy sleep"""
        if RTC is not None:
            return self.__rtc_stop()
        else:
            return self.__timer_stop()