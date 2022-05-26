import uos
import uzlib
import ql_fs
import ujson
import utime
import osTimer
import quecIot
try:
    import uhashlib
except:
    uhashlib = None
from misc import Power
from queue import Queue
from log import getLogger
from usr.modules.common import CloudObservable, CloudObjectModel

log = getLogger(__name__)
EVENT_CODE = {}
class QuecObjectModel(CloudObjectModel):
    """This class is queccloud object model"""
    def __init__(self, om_file="/usr/quec_object_model.json"):
        super().__init__(om_file)
        self.code_id = {}
        self.id_code = {}
        self.struct_code_id = {}
        self.init()

    def __init_value(self, om_type):
        if om_type in ("int", "enum", "date"):
            om_value = 0
        elif om_type in ("float", "double"):
            om_value = 0.0
        elif om_type == "bool":
            om_value = True
        elif om_type == "text":
            om_value = ""
        elif om_type == "array":
            om_value = []
        elif om_type == "struct":
            om_value = {}
        else:
            om_value = None
        return om_value

    def __get_property(self, om_item):
        om_item_key = om_item["code"]
        om_item_type = om_item["dataType"].lower()
        om_item_val = self.__init_value(om_item_type)
        self.id_code[om_item["id"]] = om_item["code"]
        self.code_id[om_item["code"]] = om_item["id"]
        if om_item_type == "struct":
            om_item_struct = om_item["specs"]
            om_item_val = {i["code"]: self.__init_value(i["dataType"].lower()) for i in om_item_struct}
            self.struct_code_id[om_item["code"]] = {i["code"]: i["id"] for i in om_item_struct}
        return om_item_key, om_item_val

    def __init_properties(self, om_properties):
        for om_property in om_properties:
            om_property_key, om_property_val = self.__get_property(om_property)
            setattr(self.properties, om_property_key, {om_property_key: om_property_val})

    def __init_events(self, om_events):
        for om_event in om_events:
            om_event_key = om_event["code"]
            om_event_out_put = om_event.get("outputData", [])
            om_event_val = {}
            self.id_code[om_event["id"]] = om_event["code"]
            self.code_id[om_event["code"]] = om_event["id"]
            if om_event_out_put:
                for om_property in om_event_out_put:
                    try:
                        property_id = int(om_property.get("$ref", "").split("/")[-1])
                    except:
                        continue
                    om_property_key = self.id_code.get(property_id)
                    om_property_val = getattr(self.properties, om_property_key)
                    om_property_val.update(om_property_val)
            setattr(self.events, om_event_key, {om_event_key: om_event_val})

    def init(self):
        with open(self.om_file, "rb") as f:
            cloud_object_model = ujson.load(f)
            self.__init_properties(cloud_object_model.get("properties", []))
            self.__init_events(cloud_object_model.get("events", []))

class QuecThing(CloudObservable):
    """This is a class for queccloud iot."""
    def __init__(self, pk, ps, dk, ds, server, life_time=120, mcu_name="", mcu_version="", mode=1):
        """
        1. Init parent class CloudObservable
        2. Init cloud connect params
        """
        super().__init__()
        self.__pk = pk
        self.__ps = ps
        self.__dk = dk
        self.__ds = ds
        self.__server = server
        self.__life_time = life_time
        self.__mcu_name = mcu_name
        self.__mcu_version = mcu_version
        self.__mode = mode
        self.__object_model = None
        self.__post_result_wait_queue = Queue(maxsize=16)
        self.__quec_timer = osTimer()

    def __quec_timer_cb(self, args):
        """osTimer callback to break waiting of get publish result"""
        self.__put_post_res(False)

    def __get_post_res(self):
        """Get publish result"""
        self.__quec_timer.start(1000 * 10, 0, self.__quec_timer_cb)
        res = self.__post_result_wait_queue.get()
        self.__quec_timer.stop()
        return res

    def __put_post_res(self, res):
        """Save publish result to queue"""
        if self.__post_result_wait_queue.size() >= 16:
            self.__post_result_wait_queue.get()
        self.__post_result_wait_queue.put(res)

    def __data_format(self, k, v):
        """Publish data format by AliObjectModel"""
        k_id = None
        struct_info = {}
        if hasattr(self.__object_model.properties, k):
            k_id = self.__object_model.code_id[k]
            if self.__object_model.struct_code_id.get(k):
                struct_info = self.__object_model.struct_code_id.get(k)
        elif hasattr(self.__object_model.events, k):
            k_id = self.__object_model.code_id[k]
            event_struct_info = hasattr(self.__object_model.events, k)
            for i in event_struct_info:
                if isinstance(getattr(self.__object_model.properties, i), dict):
                    struct_info[i] = self.__object_model.struct_code_id(i)
                else:
                    struct_info[i] = self.__object_model.code_id[i]
        else:
            return False

        log.debug("__data_format struct_info: %s" % str(struct_info))
        if isinstance(v, dict):
            nv = {}
            for ik, iv in v.items():
                if isinstance(struct_info.get(ik), int):
                    nv[struct_info[ik]] = iv
                elif isinstance(struct_info.get(ik), dict):
                    if isinstance(iv, dict):
                        nv[self.__object_model.code_id[ik]] = {struct_info[ik][ivk]: ivv for ivk, ivv in iv.items()}
                    else:
                        nv[self.__object_model.code_id[ik]] = iv
                else:
                    nv[ik] = iv
            v = nv
        return {k_id: v}

    def __event_cb(self, data):
        res_datas = []
        event = data[0]
        errcode = data[1]
        eventdata = b""
        if len(data) > 2:
            eventdata = data[2]
        log.info("[Event-ErrCode-Msg][%s][%s][%s] EventData[%s]" % (event, errcode, EVENT_CODE.get(event, {}).get(errcode, ""), eventdata))
        if event == 4:
            if errcode == 10200:
                self.__put_post_res(True)
            elif errcode == 10210:
                self.__put_post_res(True)
            elif errcode == 10220:
                self.__put_post_res(True)
            elif errcode == 10300:
                self.__put_post_res(False)
            elif errcode == 10310:
                self.__put_post_res(False)
            elif errcode == 10320:
                self.__put_post_res(False)

    def set_object_model(self, object_model):
        """Register QuecObjectModel to this class"""
        if object_model and isinstance(object_model, QuecObjectModel):
            self.__object_model = object_model
            return True
        return False

    def init(self, enforce=False):
        """queccloud connect"""
        log.debug(
            "[init start] enforce: %s QuecThing Work State: %s, quecIot.getConnmode(): %s"
            % (enforce, quecIot.getWorkState(), quecIot.getConnmode())
        )
        log.debug("[init start] PK: %s, PS: %s, DK: %s, DS: %s, SERVER: %s" % (self.__pk, self.__ps, self.__dk, self.__ds, self.__server))
        if enforce is False:
            if self.get_status():
                return True

        quecIot.init()
        quecIot.setEventCB(self.__event_cb)
        quecIot.setProductinfo(self.__pk, self.__ps)
        if self.__dk or self.__ds:
            quecIot.setDkDs(self.__dk, self.__ds)
        quecIot.setServer(self.__mode, self.__server)
        quecIot.setLifetime(self.__life_time)
        quecIot.setMcuVersion(self.__mcu_name, self.__mcu_version)
        quecIot.setConnmode(1)

        count = 0
        while quecIot.getWorkState() != 8 and count < 10:
            utime.sleep_ms(200)
            count += 1

        if not self.__ds and self.__dk:
            count = 0
            while count < 3:
                dkds = quecIot.getDkDs()
                if dkds:
                    self.__dk, self.__ds = dkds
                    log.debug("dk: %s, ds: %s" % dkds)
                    break
                count += 1
                utime.sleep(count)

        log.debug("[init over] QuecThing Work State: %s, quecIot.getConnmode(): %s" % (quecIot.getWorkState(), quecIot.getConnmode()))
        if self.get_status():
            return True
        else:
            return False

    def close(self):
        """queccloud disconnect"""
        return quecIot.setConnmode(0)

    def get_status(self):
        """Get quectel cloud connect status"""
        return True if quecIot.getWorkState() == 8 and quecIot.getConnmode() == 1 else False

    def post_data(self, data):
        """Publish object model property, event"""
        res = True
        phymodelReport_res = quecIot.phymodelReport(2, data)
        res = self.__get_post_res()
        if res:
            v = {}
        else:
            res = False
        return res

    def device_report(self):
        return quecIot.devInfoReport([i for i in range(1, 13)])

    def ota_request(self, mp_mode=0):
        """Publish mcu and firmware ota plain request"""
        return quecIot.otaRequest(mp_mode) if mp_mode in (0, 1) else False

    def ota_action(self, action=1, module=None):
        """Publish ota upgrade start or cancel ota upgrade"""
        return quecIot.otaAction(action) if action in (0, 1, 2, 3) else False
