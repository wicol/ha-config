import datetime
import re

import pytz
import hassapi as hass

#
# MQTT Export
#
# Publishes states of entities to MQTT on change and interval
# Topic is <configurable prefix>/entity_id
# Payload is influxdb line format for easy telegraf parsing
# Measurement will default to device_class of entity (can be overridden in config)
#
# Args:
# topic_prefix: <topic_prefix> # homeassistant/states for example
# entities: # list of regexes or objects with {entity_id: <id regex>, measurement: <str>, exclude: <regex>}
#   - sensor.temperature_\d+$
#   - sensor.calibrated_outdoor_temp
#   - entity_id: input_number.outdoor_temp_offset
#     measurement: temperature
#   - entity_id: sensor\..+_battery_level$
#     exclude: sensor.(s21|bl_wic)
#     measurement: battery_level
#

class MQTTExport(hass.Hass):
    def initialize(self):
        #self.receiver = self.args['receiver_entity_id']
        #self.auto_off_timeout = self.args['auto_off_timeout']
        #self.entities = self.args['devices']
        self.config = {
            "entities": self.args["entities"],
            "topic_prefix": self.args["topic_prefix"]
        }
        self.entities = {}
        all_states = self.get_state()

        # Set state and start listeners for each device
        for entity_conf in self.config["entities"]:
            if isinstance(entity_conf, str):
                entity_id_pat = entity_conf
                entity_conf = {}
                measurement = None
            elif isinstance(entity_conf, dict):
                entity_id_pat = entity_conf["entity_id"]
                measurement = entity_conf.get("measurement")

            matches = []
            for entity_id, state in all_states.items():
                if re.search(entity_id_pat, entity_id):
                    if "exclude" in entity_conf and re.search(entity_conf["exclude"], entity_id):
                        continue
                    self.entities[entity_id] = {
                        "measurement": measurement or state["attributes"]["device_class"],
                        "friendly_name": state["attributes"]["friendly_name"]
                    }
                    
        self.listen_state(self.callback, list(self.entities.keys()), attribute="state")
        interval_time = self.get_now().replace(minute=0, second=0, microsecond=0)
        self.log("Will update every 10 mins from: %s", interval_time)
        self.run_every(self.publish_all, interval_time, 600)
        self.log("entities: %s", self.entities)
    
    def callback(self, entity_id, attribute, old, new, kwargs):
        ts = self.get_now_ts()
        self.publish(entity_id, new, timestamp=ts)

    def publish_all(self, kwargs):
        values = []
        # Collect all values first and publish after that - to narrow the window of sampling
        for entity_id in self.entities.keys():
            values.append((entity_id, self.get_state(entity_id), self.get_now_ts()))
        for entity_id, value, ts in values:
            self.publish(entity_id, value, ts)

    def publish(self, entity_id, value, timestamp=None):
        if value == "unavailable":
            self.log("%s is unavailable", entity_id)
            return
        topic = f"{self.config['topic_prefix']}/{entity_id}"
        measurement = self.entities[entity_id]["measurement"]
        # TODO? "Escape: Comma, Equals Sign, Space"
        friendly_name = self.entities[entity_id]["friendly_name"].replace(" ", "\\ ")
        #typed_value = None
        #type_indicator = ""
        #try:
        #    typed_value = int(value)
        #    type_indicator = "i"
        #except ValueError:
        #    try:
        #        typed_value = float(value)
        #    except ValueError:
        #        self.log("Failed typing %s for entity_id %s", value, entity_id)
        #        return

        nano_ts = int((timestamp or self.get_now_ts()) * 1000000000)
        payload = f"{measurement},entity_id={entity_id},friendly_name={friendly_name} value={value} {nano_ts}"
        self.log("Publishing topic: %s, payload: %s", topic, payload)
        self.call_service("mqtt/publish", topic=topic, payload=payload)

