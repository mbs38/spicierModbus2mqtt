import json

class HassConnector:
    def __init__(self, mqc, globaltopic, verbosity):
        self.mqc = mqc
        self.globaltopic = globaltopic
        self.verbosity = verbosity

    def addAll(self, referenceList):
        if(self.verbosity):
            self.removeAll(referenceList)
            print("Adding all references to Home Assistant")
        for r in referenceList:
            meta = self.addHAMeta(r)

            if "r" in r.rw and not "w" in r.rw:
                if r.poller.dataType == "bool":
                    self.addBinarySensor(r, meta)
                if r.poller.dataType == "int16":
                    self.addSensor(r, meta)
            if "w" in r.rw and "r" in r.rw:
                if r.poller.dataType == "bool":
                    self.addSwitch(r, meta)
                if r.poller.dataType == "int16": #currently I have no idea what entity type to use here..
                    self.addSensor(r, meta)

    def addHAMeta(self, ref):
        config = {}
        if ref.state_class:
            config["state_class"] = ref.state_class

        if ref.device_class:
            config["device_class"] = ref.device_class

        if ref.unit_of_measurement:
            config["unit_of_measurement"] = ref.unit_of_measurement
 
        if ref.name:
            config["name"] = f"{ref.device.description} {ref.name}"
       
        return config

    def addBinarySensor(self, ref, meta):
        if(self.verbosity):
            print(f"Adding binary sensor {ref.topic} to HASS")

        object_id = f"{ref.device.name}_{ref.topic}"
        config = {"name": object_id, "object_id": object_id, "state_topic": f"{self.globaltopic}{ref.device.name}/state/{ref.topic}", "payload_on": True, "payload_off": False}
        config.update(meta)

        self.mqc.publish(f"homeassistant/binary_sensor/{self.globaltopic[0:-1]}_{ref.device.name}_{ref.topic}/config", json.dumps(config), qos=0, retain=True)

    def addSensor(self, ref, meta):
        if(self.verbosity):
            print(f"Adding sensor {ref.topic} to HASS")

        object_id = f"{ref.device.name}_{ref.topic}"
        config = {"name": object_id, "object_id": object_id, "state_topic": f"{self.globaltopic}{ref.device.name}/state/{ref.topic}"}
        config.update(meta)

        self.mqc.publish(f"homeassistant/sensor/{self.globaltopic[0:-1]}_{ref.device.name}_{ref.topic}/config", json.dumps(config), qos=0, retain=True)

    def addSwitch(self, ref, meta):
        if(self.verbosity):
            print(f"Adding switch {ref.topic} to HASS")

        object_id = f"{ref.device.name}_{ref.topic}"
        config = {"name": object_id, "object_id": object_id, "state_topic": f"{self.globaltopic}{ref.device.name}/set/{ref.topic}", "payload_on": True, "payload_off": False}
        config.update(meta)

        self.mqc.publish(f"homeassistant/switch/{self.globaltopic[0:-1]}_{ref.device.name}_{ref.topic}/config", json.dumps(config), qos=0, retain=True)

    def removeAll(self,referenceList):
        for ref in referenceList:
            self.mqc.publish(f"{self.globaltopic}{ref.device.name}/state/{ref.topic}","",qos=0)

