import datetime
import pytz

import hassapi as hass

class HeatScheduling(hass.Hass):
    def initialize(self):
        self.listen_event(self.callback, "run_heat_scheduling")
        
    def callback(self, event_name, data, kwargs):
        attr = "raw_today" if datetime.datetime.now().hour < 23 else "raw_tomorrow"
        prices = self.get_state("sensor.nordpool_kwh_se3_sek_0_07_025", attribute=attr)

        cheap = self.get_prices(prices, reverse=False)
        cheap_hours = [datetime.datetime.fromisoformat(p["start"]).strftime("%H:%M") for p in cheap] 
        cheap_hours_str = ",".join(cheap_hours)
        self.log(f"Setting heating_cheap_hours to {cheap_hours_str}")
        self.set_textvalue("input_text.heating_cheap_hours", cheap_hours_str)

        expensive = self.get_prices(prices, reverse=True)
        expensive_hours = [datetime.datetime.fromisoformat(p["start"]).strftime("%H:%M") for p in expensive] 
        expensive_hours_str = ",".join(expensive_hours)
        self.log(f"Setting heating_expensive_hours to {expensive_hours_str}")
        self.set_textvalue("input_text.heating_expensive_hours", expensive_hours_str)

    def get_prices(self, today, reverse: bool):
        for p in today:
            p["value"] = round(p["value"], -1)
        prices = []
        for i in range(4):
            if i%2:
                today = list(reversed(today))
            most = sorted(today, key=lambda p: p["value"], reverse=reverse)[0]
            most_index = today.index(most)
            prices.append(today.pop(most_index))
        prices.sort(key=lambda p: p['start'])
        return prices

