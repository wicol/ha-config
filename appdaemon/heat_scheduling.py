import datetime
import pytz

import hassapi as hass

class HeatScheduling(hass.Hass):
    def initialize(self):
        self.listen_event(self.callback, "run_heat_scheduling")
        
    def callback(self, event_name, data, kwargs):
        attr = "raw_today" if datetime.datetime.now().hour < 23 else "raw_tomorrow"
        prices = self.get_state("sensor.nordpool_kwh_se3_sek_0_07_025", attribute=attr)


        #self.log("prices: {}".format([p["value"] for p in prices]))

        cheap_am = self.get_prices(prices[:12], 2, reverse=False)
        cheap_pm = self.get_prices(prices[12:], 2, reverse=False)
        cheap = cheap_am + cheap_pm
        cheap_hours = [datetime.datetime.fromisoformat(p["start"]).strftime("%H:%M") for p in cheap] 
        cheap_hours_str = ",".join(cheap_hours)
        self.log(f"Setting heating_cheap_hours to {cheap_hours_str}")
        self.set_textvalue("input_text.heating_cheap_hours", cheap_hours_str)

        expensive_am = self.get_prices(prices[:12], 2, reverse=True)
        expensive_pm = self.get_prices(prices[12:], 2, reverse=True)
        expensive = expensive_am + expensive_pm
        expensive_hours = [datetime.datetime.fromisoformat(p["start"]).strftime("%H:%M") for p in expensive] 
        expensive_hours_str = ",".join(expensive_hours)
        self.log(f"Setting heating_expensive_hours to {expensive_hours_str}")
        self.set_textvalue("input_text.heating_expensive_hours", expensive_hours_str)

    #def f(self, p):
    #    return "{}-{}".format(datetime.datetime.fromisoformat(p["start"]).strftime("%H:%M"), p["value"])
    
    def get_prices(self, prices, count, reverse: bool):
        # Prices: [{"start": "isodatetime", "end": "isodatetime", "value": int}]
        # Round to nearest 10
        prices = prices.copy()
        results = []

        for p in prices:
            p["value"] = round(p["value"], -1)
        #self.log("rounded prices: {}".format([p["value"] for p in prices]))

        for i in range(count):
            #self.log("prices: {}".format([self.f(p) for p in prices]))
            # Sort by price keeping internal date sorting
            prices_sorted = sorted(prices, key=lambda p: p["value"], reverse=reverse)
            #self.log("prices_sorted: {}".format([self.f(p) for p in prices_sorted]))
            most = sorted(prices, key=lambda p: p["value"], reverse=reverse)[0]
            #self.log(f"most: {self.f(most)}")
            most_index = prices.index(most)
            results.append(prices.pop(most_index))
            
            # Reverse date sorting to search from other end of span next iteration
            prices = list(reversed(prices))

        results.sort(key=lambda p: p['start'])
        return results

