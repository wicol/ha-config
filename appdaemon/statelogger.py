import appdaemon.plugins.hass.hassapi as hass


class StateLogger(hass.Hass):
    def initialize(self):
        #group = self.get_state('group.xiaomi_sensors', 'all')
        #entity_ids = group['attributes']['entity_id']
        entity_ids = [
            #'binary_sensor.cam_01_motion',
            #'sensor.temperature_158d0001b8d3d5',
            #'sensor.temperature_158d0001b8d57d',
            #'binary_sensor.motion_sensor_158d00016db717'
            'media_player.denon_3300',
            'media_player.bio',
            'media_player.kodi',
            'binary_sensor.ps3',
            'binary_sensor.xbox360'
        ]
        self.log('Logging state changes for {}'.format(', '.join(entity_ids)))
        for entity_id in entity_ids:
            #friendly_name = self.friendly_name(entity_id)
            self.listen_state(self.log_state, entity_id, attribute='all') #, friendly_name=friendly_name)

    def log_state(self, entity_id, attribute, old, new, kwargs):
        #state = self.get_state(entity_id, 'all')
        old_attributes = old.pop('attributes')
        new_attributes = new.pop('attributes')

        attributes_str = '\n'.join(
            ['    {}: {} > {}'.format(k, v, new_attributes.get(k, None)) for k, v in old_attributes.items()]
        )
        self.log(
            '{} changed:\n{}\n{}'.format(
                entity_id,
                '\n'.join([
                    '    {}: {} > {}'.format(k, v, new.get(k, None)) for k, v in old.items()
                ]),
                attributes_str
            )
        )

