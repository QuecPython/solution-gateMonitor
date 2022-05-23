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


class SYSConfig(object):

    class _cloud(object):
        none = 0x0
        quecIot = 0x1

    debug = True

    log_level = "DEBUG"

    cloud = _cloud.quecIot

    checknet_timeout = 60

    base_cfg = {
        "LocConfig": True,
    }

    device_cfg = True
    usr_cfg = True
