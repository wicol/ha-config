import datetime
import pytz

import hassapi as hass

#
# Denon AVR auto source/off
#
# Args:
# receiver_entity_id: <entity id of receiver>
# auto_off_timeout: <seconds> # turn off receiver n seconds after last device is turned off
# devices:
#   <entity_id>:
#     # "on"-states for this device
#     states: ['playing', 'paused']
#     # receivers source name for this device
#     source: HTPC
#   <entity_id2>:
#     ...
#

class DenonAuto(hass.Hass):
    def initialize(self):
        self.receiver = self.args['receiver_entity_id']
        self.auto_off_timeout = self.args['auto_off_timeout']
        self.devices = self.args['devices']

        # Set state and start listeners for each device
        for entity_id, entity_data in self.devices.items():
            entity_data['active'] = self.get_state(entity_id) in entity_data['states']
            self.listen_state(self.active_handler, entity_id)
            self.listen_state(self.inactive_handler, entity_id, duration=self.auto_off_timeout)
        self.log(f'devices: {self.devices}')
        #self.log('Listening to entities: {}'.format(', '.join(self.devices.keys())))
    
    def active_devices(self):
        return [device for device, config in self.devices.items() if config.get('active')]
    
    def active_handler(self, entity_id, attribute, old, new, kwargs):
        if old == new:
            return
        self.log(f'{entity_id} went from {old} to {new}')
        if new in self.devices[entity_id]['states']:
            # Device is active
            # If it's got a source and no other devices are active - switch source!
            if 'source' in self.devices[entity_id] and not self.active_devices():
                self.select_source(self.devices[entity_id]['source'])
            
            # Mark device as active (doesn't matter if we switched to it)
            self.devices[entity_id]['active'] = True
            
    def inactive_handler(self, entity_id, attribute, old, new, kwargs):
        if old == new or not self.devices[entity_id]['active']:
            return
        # Devices new state is not considered active
        self.log(f'{entity_id} went from {old} to {new} {self.auto_off_timeout}s ago')

        if new not in self.devices[entity_id]['states']:
            self.devices[entity_id]['active'] = False

        if self.get_state(self.receiver) == 'off':
            # It's already off
            return
        
        active_entities = self.active_devices()
        if active_entities:
            self.log(f'Entities still active: {active_entities}')
            return
        
        self.log('All devices have been off for {}s - turning off receiver'.format(self.auto_off_timeout))
        self.turn_off(self.receiver)
        
    def select_source(self, source):
        current_source = self.get_state(self.receiver, attribute='source')
        if current_source == source:
            return
        self.log(f'Switching to source: {source}')
        self.call_service(
            'media_player/select_source',
            entity_id=self.receiver,
            source=source
        )

