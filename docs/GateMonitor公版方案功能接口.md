# GateMonitor 公版方案功能接口

## GateMonitor 功能模块说明

### 功能模块说明

#### 业务功能模块

| 模块名称       | 模块功能                                                     |
| -------------- | ------------------------------------------------------------ |
| GateMonitor    | 业务逻辑模块，主要负责处理所有告警功能需求。                 |
| InterruptEvent | 中断事件接收模块，负责触发外部中断后的事件处理调度。         |
| DeviceCheck    | 设备状态检测状态模块，主要负责检测网络以及其他设备状态。     |
| Settings       | 配置参数读写模块。                                           |
| Controller     | 控制器模块，主要用于设备功能模块的控制，如电源的重启与关机，LED的亮灭控制，蜂鸣器控制，配置文件的写入保存，云端消息的发送等。 |
| Collector      | 设备业务逻辑执行模块，主要用于设备开机以及设备状态提示。     |

#### 设备功能模块

| 模块名称        | 模块功能                                                     |
| --------------- | ------------------------------------------------------------ |
| Buzzer          | 控制设备蜂鸣器                                               |
| LED             | 控制设备LED                                                  |
| History         | 历史文件读写操作模块                                         |
| Battery         | 电池模块，获取电池电量与电压                                 |
| LowEnergyManage | 低功耗唤醒模块，用于设置不同级别的低功耗模型，定时唤醒模块进行业务工作。 |
| QuecThing       | 移远云模块，主要用于与云端的消息交互与OTA升级                |
| QuecObjectModel | 移远云物模型抽象类，将移远云导出的物模型（json格式）抽象为一个类进行功能使用 |
| RemotePublish   | 云端消息发布类，用于兼容不同云的消息发布与OTA升级检测与确认  |

## GateMonitor API v1.0

### settings

> 该模块为配置参数模块

- 项目配置主要分为三个大块
  - 系统配置模块:
    * SYSConfig
  - 用户配置模块:
    * UserConfig
  - 云端配置配置:
    * QuecCloudConfig
  - 设备状态初始配置：
    - DeviceConfig
- 该模块将配置好的模块设置集成到一个`DICT`中，可通过`settings.get()`方式获取到具体配置参数
- 全局变量:
  + `PROJECT_NAME` -- 项目名称
  + `PROJECT_VERSION` -- 项目版本
  + `DEVICE_FIRMWARE_NAME` -- 设备版本
  + `DEVICE_FIRMWARE_VERSION` -- 固件版本

#### 全局变量导入

例:

```python
from usr.settings import PROJECT_NAME
from usr.settings import PROJECT_VERSION
from usr.settings import DEVICE_FIRMWARE_NAME
from usr.settings import DEVICE_FIRMWARE_VERSION
```

#### settings 导入

例:

```python
from usr.settings import settings
```

#### init 初始化

> 功能:
>
> - 检查持久化配置文件是否存在，存在则直接读取配置文件配置
> - 若不存在则读取`SYSConfig`设置参数, 根据配置读取用户配置与功能配置
> - 读取完成所有配置参数后，将配置参数写入配置文件中持久化存储

例:

```python
res = settings.init()
```

参数:

无

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### get 获取配置参数

例:

```python
current_settings = settings.get()
```

参数:

无

返回值:

| 数据类型 | 说明     |
| :------- | -------- |
| DICT     | 配置参数 |

```json
{
    "sys":{
        "log_level":"DEBUG",
        "checknet_timeout":60,
        "device_cfg":true,
        "debug":true,
        "base_cfg":{
            "LocConfig":true
        },
        "usr_cfg":true,
        "cloud":1
    },
    "cloud":{
        "LIFETIME":65500,
        "SERVER":"http://iot-south.quectel.com:5683",
        "DK":"",
        "DS":"",
        "MODE":0,
        "PK":"",
        "PS":""
    },
    "device_cfg":{
        "doorState":1,
        "lowPowerAlarm":0
    },
    "usr_cfg":{
        "rtc_wakeup_period":43200
    }
}
```

#### set 设置配置参数

> 配置参数标识符列表，见  `UserConfig` 具体属性

例:

```python
opt = 'doorState'
val = 1
res = settings.set(opt, val)
```

参数:

| 参数 | 类型                 | 说明           |
| :--- | -------------------- | -------------- |
| opt  | STRING               | 配置参数标识符 |
| val  | STRING/BOOL/INT/DICT | 配置参数属性值 |

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### save 持久化保存配置参数

> 将配置参数写入文件进行持久化保存，文件名全路径`/usr/gateMonitor_settings.json`

例:

```python
res = settings.save()
```

参数:

无

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### remove 删除配置参数文件

例:

```python
res = settings.remove()
```

参数:

无

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### reset 重置配置参数

> 先移除配置参数文件, 再重新生成配置参数文件

例:

```python
res = settings.reset()
```

参数:

无

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

### SYSConfig

> 系统配置参数，主要用于配置debug日志的开启关闭，日志等级，使用的云平台，基础模块启用设置，用户配置启用设置。
> 用户只用在对应的配置模块中将配置参数录入完整之后，调用`settings`模块进行初始化即可集成所有配置参数和配置文件。

> 系统配置参数列表

| 参数             | 类型   | 说明                                                         |
| ---------------- | ------ | ------------------------------------------------------------ |
| debug            | BOOL   | 是否开启debug日志,True - 开启,False - 关闭                   |
| log_level        | STRING | 日志等级,debug,info,warn,error,critical                      |
| cloud            | INT    | 项目使用云平台,0 - none,1 - quecIot                          |
| checknet_timeout | INT    | 网络检测超时时间，单位s，默认60s                             |
| base_cfg         | DICT   | 基础模块启用配置,key：为模块配置名称,value：是否启用,True - 启用,False - 禁用 |
| user_cfg         | BOOL   | 是否启用用户具体业务配置文件,True - 开启,False - 关闭        |

> `base_cfg` 样例

```json
{
    "LocConfig": true,
}
```

> 系统配置参数枚举值

SYSConfig.\_cloud 支持云服务列表

| KEY     | VALUE | 说明   |
| ------- | ----- | ------ |
| none    | 0x0   | 无     |
| quecIot | 0x1   | 移远云 |

### QuecCloudConfig

> 移远云模块初始化配置参数

> 移远云模块配置参数列表

| 参数     | 类型   | 说明                                                         |
| -------- | ------ | ------------------------------------------------------------ |
| PK       | STRING | ProductKey产品标识                                           |
| PS       | STRING | ProductSecret产品密钥                                        |
| DK       | STRING | DeviceName设备名称, 默认空                                   |
| DS       | STRING | DeviceSecret设备密钥, 默认空                                 |
| SERVER   | STRING | 可选参数,需要连接的服务器名称,默认为                         |
| LIFETIME | INT    | 通信之间允许的最长时间段（以秒为单位）,默认为65500，范围（120-65500） |

### UsrConfig

> 用户模块初始化配置参数

> 用户模块配置参数列表

| 参数              | 类型 | 说明                         |
| ----------------- | ---- | ---------------------------- |
| rtc_wakeup_period | int  | RTC定时唤醒时间，默认为43200 |

### DeviceConfig

> 设备模块初始化配置参数

> 设备模块配置参数列表

| 参数          | 类型 | 说明                                        |
| ------------- | ---- | ------------------------------------------- |
| doorState     | int  | 初始开关门状态，0：开门，1：关门，默认为0   |
| lowPowerAlarm | int  | 低电量告警状态，0：未告警，1：告警，默认为0 |

### Collector

> 设备业务逻辑执行模块，主要用于设备开机以及设备状态提示。

#### Collector 导入

例:

```python
from usr.gateMonitor_controller import Collector

collector = Collector()
```

#### add_module 注册功能模块

> 可注册模块:
>
> - `Controller`
> - `DeviceCheck`
>
> 业务功能:
>
> 将控制器模块以注册的方式添加进设备业务逻辑模块

例:

```python
from usr.gateMonitor_controller import Controller
controller = Controller()
collector.add_module(controller)
```

参数:

| 参数   | 类型   | 说明     |
| ------ | ------ | -------- |
| module | object | 模块对象 |

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### device_status_get 设备模块状态获取

> 依赖模块:
>
> - `DeviceCheck`
> - `Controller`
>
> 业务功能:
>
> 获取设备状态，当前只返回注网状态，并控制设备做出对应指示

例：

```python
res = collector.device_status_get()
```

参数:

无

返回值:

| 数据类型 | 说明         |
| :------- | ------------ |
| BOOL     | 设备注网状态 |

### Controller 

> 控制器模块，主要用于控制各个功能模块，如电源关闭与重启，发送数据等。

#### Collector 导入

例:

```python
from usr.gateMonitor_controller import Controller
controller = Controller()
```

#### add_module 注册功能模块

> 可注册模块:
>
> - `LED`
> - `Buzzer`
> - `Battery`
> - `RemotePublish`
> - `Settings`
> - `LowEnergyManage`
>
> 业务功能:
>
> 将控制器模块以注册的方式添加进设备业务逻辑模块

例:

```python
from machine import Pin
from usr.modules.peripherals import Buzzer
buzzer = Buzzer(Pin.GPIOn)
controller.add_module(buzzer)
```

参数:

| 参数   | 类型   | 说明     |
| ------ | ------ | -------- |
| module | object | 模块对象 |

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### settings_set 配置信息修改

> 依赖模块:
>
> - `Settings`
>
> 业务功能:
>
> - 用于修改用户业务配置参数

例:

```python
controller.settings_set(key, value)
```

参数:

| 参数  | 类型            | 说明     |
| ----- | --------------- | -------- |
| key   | STRING          | 属性名称 |
| value | STRING/INT/DICT | 属性值   |

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### settings_save 配置信息持久化保存

> 依赖模块:
>
> - `Settings`
>
> 业务功能:
>
> - 用于将修改后的配置参数持久化存储到文件中

例:

```python
controller.settings_save()
```

参数:

无

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### power_restart 设备电源重启

> 依赖模块:
>
> - `Power`
>
> 业务功能:
>
> - 调用电源模块接口重启设备

例:

```python
controller.power_restart()
```

参数:

无

返回值:

无

#### power_down 设备关机

> 依赖模块:
>
> - `Power`
>
> 业务功能:
>
> - 调用电源模块接口关机设备

例:

```python
controller.power_down()
```

参数:

无

返回值:

无

#### remote_post_data 云端消息发布

> 依赖模块:
>
> - `RemotePublish`
>
> 业务功能:
>
> - 调用`RemotePublish.post_data`接口发布消息

例:

```python
controller.remote_post_data(data)
```

参数:

| 参数 | 类型 | 说明                                                  |
| ---- | ---- | ----------------------------------------------------- |
| data | DICT | 发送消息集合, 即`collector.device_data_get()`的返回值 |

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### remote_ota_check OTA升级计划查询

> 依赖模块:
>
> - `RemotePublish`

例:

```python
res = controller.remote_ota_check()
```

参数:

无

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### remote_ota_action OTA升级确认

> 依赖模块:
>
> - `RemotePublish`

例:

```python
res = controller.remote_ota_action(action, module)
```

参数:

| 参数   | 类型   | 说明                                                         |
| ------ | ------ | ------------------------------------------------------------ |
| action | INT    | 0 - 取消升级，1 - 确认升级                                   |
| module | STRING | 升级模块，设备版本`DEVICE_FIRMWARE_NAME`或项目名称`PROJECT_NAME` |

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### low_energy_init 低功耗模块唤醒初始化

> 依赖模块:
>
> - `LowEnergyManage`

例:

```python
res = controller.low_energy_init()
```

参数:

无

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### low_energy_start 低功耗模块唤醒启动

> 依赖模块:
>
> - `LowEnergyManage`

例:

```python
res = controller.low_energy_start()
```

参数:

无

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### led_on 使能LED

> 依赖模块:
>
> - `LED`

例:

```python
controller.led_on(mode=1)
```

参数:

| 参数 | 类型 | 说明                     |
| ---- | ---- | ------------------------ |
| mode | INT  | 0 - 蓝色LED，1 - 红色LED |

返回值:

无

#### led_off 关闭LED

> 依赖模块:
>
> - `LED`

例:

```python
controller.led_off(mode=1)
```

参数:

| 参数 | 类型 | 说明                     |
| ---- | ---- | ------------------------ |
| mode | INT  | 0 - 蓝色LED，1 - 红色LED |

返回值:

无

#### led_flicker_on 打开LED闪烁

> 依赖模块:
>
> - `LED`

例:

```python
controller.led_flicker_on(on_period, off_period, count, mode)
```

参数:

| 参数       | 类型 | 说明                                       |
| ---------- | ---- | ------------------------------------------ |
| on_period  | INT  | LED打开时间，单位ms                        |
| off_period | INT  | LED关闭时间，单位ms                        |
| count      | INT  | LED一开一关为一次闪烁，count为需要闪烁次数 |
| mode       | INT  | 0 - 蓝色LED，1 - 红色LED                   |

返回值:

无

#### led_flicker_off 关闭LED闪烁

> 依赖模块:
>
> - `LED`

例:

```python
controller.led_flicker_off()
```

参数:

无

返回值:

无

#### buzzer_flicker_on 打开蜂鸣器

> 依赖模块:
>
> - `Buzzer`

例:

```python
controller.buzzer_flicker_on(on_period, off_period, count)
```

参数:

| 参数       | 类型 | 说明                                      |
| ---------- | ---- | ----------------------------------------- |
| on_period  | INT  | Buzzer打开时间，单位ms                    |
| off_period | INT  | Buzzer关闭时间，单位ms                    |
| count      | INT  | Buzzer一开一关为一次，count为需要响铃次数 |

返回值:

无

#### buzzer_flicker_off 关闭蜂鸣器

> 依赖模块:
>
> - `Buzzer`

例:

```python
controller.buzzer_flicker_off()
```

参数:

无

返回值:

无

#### get_device_voltage 获取设备电量

> 依赖模块:
>
> - `Battery`

例:

```python
controller.get_device_voltage()
```

参数:

无

返回值:

| 数据类型 | 说明       |
| -------- | ---------- |
| INT      | 电量百分比 |

#### get_net_csq 获取设备信号值

> 依赖模块:
>
> - `net`

例:

```python
controller.get_net_csq()
```

参数:

无

返回值:

| 数据类型 | 说明         |
| -------- | ------------ |
| INT      | 设备信号强度 |

#### get_cloud_status 获取设备连云状态

> 依赖模块:
>
> - `quecIot`

例:

```python
controller.get_cloud_status()
```

参数:

无

返回值:

| 数据类型 | 说明                                          |
| -------- | --------------------------------------------- |
| BOOL     | cloud连接状态， True 连接成功；False 连接失败 |

#### append_repord_data 添加待上报数据

> 依赖模块:
>
> - `内置函数`
> - 该函数添加注网未成功前触发的事件数据，待注网成功后发送

例:

```python
controller.append_repord_data(data)
```

参数:

| 参数 | 类型 | 说明                                                         |
| ---- | ---- | ------------------------------------------------------------ |
| data | LIST | 待上报数据，注网未成功前触发的事件数据，待注网成功后发送；[{k:v}, {k,v}] |

返回值:

无

#### remove_repord_data 清除待上报数据

> 依赖模块:
>
> - `内置函数`
> - 该函数清除注网未成功前触发的事件数据

例:

```python
controller.remove_repord_data()
```

参数:

无

返回值:

无

#### check_repord_data 检查待上报数据

> 依赖模块:
>
> - `内置函数`
> - 检查是否有待上报数据，若有则上报

例:

```python
controller.check_report_data()
```

参数:

无

返回值:

无

### DeviceCheck

> 设备状态检测状态模块

#### DeviceCheck 导入

例:

```python
from usr.gateMonitor_controller import DeviceCheck
device = DeviceCheck()
```

#### wait_net_state 等待注网

> 依赖模块:
>
> - `CheckNetwork`

例:

```python
device.wait_net_state()
```

参数:

无

返回值:

| 数据类型 | 说明                           |
| -------- | ------------------------------ |
| BOOL     | 注网成功返回True,反之返回False |

### GateMonitor

> 主业务逻辑

#### GateMonitor 导入

例:

```python
from usr.gateMonitor import GateMonitor
gateMonitor = GateMonitor()
```

#### add_module 注册功能模块

> 可注册模块:
>
> - `Controller`
> - `InterruptEvent`
> - 业务功能: 将控制器模块以注册的方式添加进主业务逻辑模块
>

例:

```python
from usr.gateMonitor_controller import Controller
controller = Controller()
gateMonitor.add_module(controller)
```

参数:

| 参数   | 类型   | 说明     |
| ------ | ------ | -------- |
| module | object | 模块对象 |

返回值:

| 数据类型 | 说明                    |
| :------- | ----------------------- |
| BOOL     | `True`成功, `False`失败 |

#### deviceAlarm 设备开关门告警

> 依赖模块:
>
> - `GateMonitor`
> - 设备开关门告警处理

例:

```python
gateMonitor.deviceAlarm(topic, params)
```

参数:

| 参数   | 类型 | 说明                                                         |
| ------ | ---- | ------------------------------------------------------------ |
| topic  | int  | 采用sys_bus发布订阅的方式执行，此topic为订阅主题，在执行sys_bus.publish(topic, params)的时候传进来即可 |
| params | dict | 采用sys_bus发布订阅的方式执行，此params为携带参数，在执行sys_bus.publish(topic, params)的时候传进来即可 |

返回值:

无

#### periodicHeartbeat 业务心跳

> 依赖模块:
>
> - `GateMonitor`
> - 业务心跳，12h/次

例:

```python
gateMonitor.periodicHeartbeat(topic, params)
```

参数:

| 参数   | 类型 | 说明                                                         |
| ------ | ---- | ------------------------------------------------------------ |
| topic  | int  | 采用sys_bus发布订阅的方式执行，此topic为订阅主题，在执行sys_bus.publish(topic, params)的时候传进来即可 |
| params | dict | 采用sys_bus发布订阅的方式执行，此params为携带参数，在执行sys_bus.publish(topic, params)的时候传进来即可 |

返回值:

无

#### manualAlarm SOS一键告警

> 依赖模块:
>
> - `GateMonitor`
> - SOS一键告警

例:

```python
gateMonitor.manualAlarm(topic, params)
```

参数:

| 参数   | 类型 | 说明                                                         |
| ------ | ---- | ------------------------------------------------------------ |
| topic  | int  | 采用sys_bus发布订阅的方式执行，此topic为订阅主题，在执行sys_bus.publish(topic, params)的时候传进来即可 |
| params | dict | 采用sys_bus发布订阅的方式执行，此params为携带参数，在执行sys_bus.publish(topic, params)的时候传进来即可 |

返回值:

无

#### lowPowerAlarm 低电量告警

> 依赖模块:
>
> - `GateMonitor`
> - 低电量告警

例:

```python
gateMonitor.lowPowerAlarm(topic, params)
```

参数:

| 参数   | 类型 | 说明                                                         |
| ------ | ---- | ------------------------------------------------------------ |
| topic  | int  | 采用sys_bus发布订阅的方式执行，此topic为订阅主题，在执行sys_bus.publish(topic, params)的时候传进来即可 |
| params | dict | 采用sys_bus发布订阅的方式执行，此params为携带参数，在执行sys_bus.publish(topic, params)的时候传进来即可 |

返回值:

无

#### deviceWakeUp 设备唤醒

> 依赖模块:
>
> - `GateMonitor`

例:

```python
gateMonitor.deviceWakeUp()
```

参数:

无

返回值:

无

#### powerOnManage 注网成功后事件处理

> 依赖模块:
>
> - `GateMonitor`

例:

```python
gateMonitor.powerOnManage(cloud_sta)
```

参数:

| 参数      | 类型 | 说明           |
| --------- | ---- | -------------- |
| cloud_sta | BOOL | 连接云平台状态 |

返回值:

无

#### makeFunctions 注册任务事件到sys_bus

> 依赖模块:
>
> - `GateMonitor`

例:

```python
gateMonitor.makeFunctions()
```

参数:

无

返回值:

无

### InterruptEvent

> 外部中断事件接收处理

#### InterruptEvent 导入

例:

```python
from usr.gateMonitor import InterruptEvent
extint = InterruptEvent()
```

#### __magnetCallback 开关门中断回调

> 依赖模块:
>
> - `InterruptEvent`

无需主动执行，中断触发会自动触发该回调函数。

#### __keyCallback SOS中断回调

> 依赖模块:
>
> - `InterruptEvent`

无需主动执行，中断触发会自动触发该回调函数。

#### get_key_gpio_level 读取SOS引脚电平

> 依赖模块:
>
> - `InterruptEvent`

例:

```python
extint.get_key_gpio_level()
```

参数:

无

返回值:

| 数据类型 | 说明     |
| -------- | -------- |
| INT      | 电平高低 |

#### runTask 运行监测回调任务

> 依赖模块:
>
> - `InterruptEvent`

例:

```python
extint.runTask()
```

参数:

无

返回值:

无

#### interruptManage  中断回调处理

> 依赖模块:
>
> - `InterruptEvent`

例:

```python
extint.runTask()
```

参数:

无

返回值:

无