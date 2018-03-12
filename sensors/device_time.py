#!/usr/bin/env python3
"""
Print total time in minutes spent in a state for an entity_id
"""
import sys
import datetime
import click
from influxdb import InfluxDBClient

@click.command()
@click.option(
    '--date',
    default=datetime.datetime.utcnow().strftime('%Y%m%d'),
    help='Get value for specific date. Format: "YYYYMMDD". Defaults to today.'
)
@click.option('--states', default='on',
    help='What states? (Value of --field-key). Separate with ",". Defaults to "on".')
@click.option('--field-key', default='state',
    help='Name of the field key that contains the state. Defaults to "state".')
@click.option('--last-session', is_flag=True)
@click.option('--max-pause-seconds', default=300)
@click.option('--debug', is_flag=True)
@click.argument('database')
@click.argument('measurement')
@click.argument('tag_key')
@click.argument('tag_value')
def get_time_in_state(
        database, measurement, tag_key, tag_value, date, states,
        field_key, last_session, max_pause_seconds, debug):
    """
    Get minutes spent in <state> for a device and date. (<state> defaults to 'on').
    Provide DATABASE, MEASUREMENT, TAG_KEY and TAG_VALUE to create a query like:
    SELECT <field-key> FROM <MEASUREMENT> WHERE <TAG_KEY> = '<TAG_VALUE>'
   
    \b
    Example invocation:
    device_time.py --date 20180301 telegraf device_log entity_id sony_bravia_tv
    """
    # Init
    # TODO: credentials, host
    client = InfluxDBClient(database=database)
    date = datetime.datetime.strptime(date, '%Y%m%d')
    states = states.split(',')
    
    state_log = []
    
    # Get last known state before date start
    initial_state_res = client.query(
        f"SELECT last({field_key}) as state FROM {measurement} WHERE {tag_key} = '{tag_value}' and time < '{date:%Y-%m-%d}';",
        epoch='ms'
    )
    if initial_state_res:
        state_log.append({
            # First period starts at the beginning of today
            'start': date,
            'state': next(initial_state_res.get_points())['state'] in states
        })
    
    # Get measurements from date
    res = client.query(
        f"SELECT {field_key} as state FROM {measurement} WHERE {tag_key} = '{tag_value}' and time > '{date:%Y-%m-%d}' and time < '{date:%Y-%m-%d}' + 1d;",
        epoch='ms'
    )

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
        point_dt = datetime.datetime.fromtimestamp(point['time']/1000)
        # Add duration and end to last state
        if state_log:
            state_log[-1].update({
                'duration': point_dt - state_log[-1]['start'],
                'end': point_dt
            })
        state_log.append({'start': point_dt, 'state': point['state'] in states})
    
    # Add duration and end to last state
    # Let it end at earliest of now or end of same day (allows for getting dates in
    # the past)
    end = min([
        datetime.datetime.now(),
        state_log[-1]['start'].replace(hour=0, minute=0, second=0, microsecond=0)
        + datetime.timedelta(days=1)
    ])
    state_log[-1].update({
        'duration': end - state_log[-1]['start'],
        'end': end
    })
    
    if last_session:
        # Slice state_log to just include last on-session, not counting
        # off-durations less than max_pause_seconds
        found_on_state = False
        for i, s in enumerate(reversed(state_log)):
            if s['state']:
                found_on_state = True
            elif found_on_state and s['duration'].total_seconds() > max_pause_seconds:
                break
        state_log = state_log[-i:]
    
    if debug:
        for s in state_log:
            print('{0:%H:%M}-{1:%H:%M} - {2} {3}m'.format(s['start'], s['end'], s['state'], int(s['duration'].total_seconds()/60)))
    
    # Print total minutes in on-state
    durations = [s['duration'] for s in state_log if s['state']]
    print(int(sum(durations, datetime.timedelta(0)).total_seconds() / 60))

if __name__ == '__main__':
   get_time_in_state()
