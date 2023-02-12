import datetime
import json
import pytz

import hassapi as hass

class EnergyUsage(hass.Hass):
    def initialize(self):
        self.run_daily(self.callback, "00:00:05")
        self.usage_data_entity = self.get_entity("input_text.energy_usage_data")

    def callback(self, kwargs):
        # fetch last_period from sensor.energy_usage_day - it has this last_period attribute which is nice
        usage_yesterday_wh = float(self.get_state("sensor.energy_usage_day", attribute="last_period") or 0)
        self.log("sensor.energy_usage_day.last_period: {}".format(usage_yesterday_wh))
        # convert to kwh
        usage_yesterday_kwh = round(usage_yesterday_wh / 1000, 1)

        # fetch data from input_text
        usage_data_str = self.usage_data_entity.get_state()
        self.log("Stored usage data: {}".format(usage_data_str))
        try:
            usage_data = [item.split(":") for item in usage_data_str.split(",")]
        except:
            self.log("Failed loading usage_data, resetting to empty")
            usage_data = []

        #try:
        #    usage_data = json.loads(usage_data_json)
        #except:
        #    self.log("Failed loading usage_data, resetting to empty")
        #    usage_data = []

        # add yesterday to the list
        usage_data.append((
            (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
            usage_yesterday_kwh
        ))

        # truncate to (last) 8 days
        usage_data = usage_data[-8:]

        # save new usage data to input_text entity
        new_usage_data_str = ",".join(["{}:{}".format(dt, val) for dt, val in usage_data])
        #self.usage_data_entity.set_state(state=json.dumps(usage_data))
        self.usage_data_entity.set_state(state=new_usage_data_str)
        self.log("Updated usage data to: {}".format(new_usage_data_str))
