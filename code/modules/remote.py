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
from log import getLogger
from usr.modules.common import Observable, CloudObserver

log = getLogger(__name__)

class RemotePublish(Observable):
    """This class is for post data to cloud"""
    def __init__(self):
        super().__init__()
        self.__cloud = None

    def __cloud_conn(self, enforce=False):
        """Cloud connect"""
        return self.__cloud.init(enforce=enforce) if self.__cloud else False

    def __cloud_post(self, data):
        """Cloud publish object model data"""
        return self.__cloud.post_data(data) if self.__cloud else False

    def add_cloud(self, cloud):
        """Add Cloud object"""
        if hasattr(cloud, "init") and \
                hasattr(cloud, "post_data") and \
                hasattr(cloud, "ota_request") and \
                hasattr(cloud, "ota_action"):
            self.__cloud = cloud
            return True
        return False

    def cloud_ota_check(self):
        """Check ota plain"""
        return self.__cloud.ota_request() if self.__cloud else False

    def cloud_ota_action(self, action=1, module=None):
        """Confirm ota upgrade"""
        return self.__cloud.ota_action(action, module) if self.__cloud else False

    def cloud_device_report(self):
        """Device & project version report"""
        return self.__cloud.device_report() if self.__cloud else False

    def cloud_rrpc_response(self, message_id, data):
        """RRPC response"""
        return self.__cloud.rrpc_response(message_id, data) if self.__cloud else False

    def post_data(self, data):
        """Data format to post:"""
        res = True
        if self.__cloud_conn():
            if not self.__cloud_post(data):
                if self.__cloud_conn(enforce=True):
                    if not self.__cloud_post(data):
                        res = False
                else:
                    log.error("Cloud Connect Failed.")
                    res = False
        else:
            log.error("Cloud Connect Failed.")
            res = False

        if res is False:
            # This Observer Is History
            self.notifyObservers(self, *[data])

        return res