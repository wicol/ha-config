#!/usr/bin/env python3
"""
Print total time in minutes spent in on-state for an entity_id
"""
import sys
import datetime
from influxdb import InfluxDBClient

# Settings
dbname = 'telegraf'
measurement = 'device_log'
entity_id = 'sony_bravia_tv'
max_pause_seconds = 300

# Init
client = InfluxDBClient(database=dbname)
now = datetime.datetime.utcnow()
#now = datetime.datetime(2018,1,4,0,0,0)
state_log = []

# Get last known state before today
initial_state_res = client.query(f"SELECT last(state) as state FROM {measurement} WHERE entity_id = '{entity_id}' and time < '{now:%Y-%m-%d}';")
if initial_state_res:
    state_log.append({
        # First period starts at the beginning of today
        'start': now.replace(hour=0, minute=0, second=0, microsecond=0),
        'state': next(initial_state_res.get_points())['state'] == 'on'
    })

# Get measurements from today
res = client.query(f"SELECT state FROM {measurement} WHERE entity_id = '{entity_id}' and time > '{now:%Y-%m-%d}' and time < '{now:%Y-%m-%d}' + 1d;")
if not res:
    # No measurements today
    print(0)
    exit(0)

# Collect timedeltas here
# Build a list of dicts: [{
#    'start': datetime,
#    'end': datetime,
#    'state': bool,
#    'duration': timedelta
# }]
for point in res.get_points():
    point_dt = datetime.datetime.strptime(point['time'][:26], '%Y-%m-%dT%H:%M:%S.%f')
    # Add duration and end to last state
    if state_log:
        state_log[-1].update({
            'duration': point_dt - state_log[-1]['start'],
            'end': point_dt
        })
    state_log.append({'start': point_dt, 'state': point['state'] == 'on'})

# Add duration and end to last state
# Let it end at earliest of now or end of same day (allows for getting dates in
# the past)
end = min([
    datetime.datetime.utcnow(),
    state_log[-1]['start'].replace(hour=0, minute=0, second=0, microsecond=0)
    + datetime.timedelta(days=1)
])
state_log[-1].update({
    'duration': end - state_log[-1]['start'],
    'end': end
})

if 'last_session' in sys.argv:
    # Slice state_log to just include last on-session, not counting
    # off-durations less than max_pause_seconds
    found_on_state = False
    for i, state in enumerate(reversed(state_log)):
        if state['state']:
            found_on_state = True
        elif found_on_state and state['duration'].total_seconds() > max_pause_seconds:
            break
    state_log = state_log[-i:]

if 'debug' in sys.argv:
    for s in state_log:
        print('{0:%H:%M}-{1:%H:%M} - {2} {3}m'.format(s['start'], s['end'], s['state'], int(s['duration'].total_seconds()/60)))

# Print total minutes in on-state
durations = [s['duration'] for s in state_log if s['state']]
print(int(sum(durations, datetime.timedelta(0)).total_seconds() / 60))
