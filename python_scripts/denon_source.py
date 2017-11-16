entity_id = data.get('entity_id', None)

device_source_map = {
    'media_player.kodi': 'HTPC',
    'binary_sensor.xbox360': 'XBOX 360',
    'binary_sensor.ps3': 'PS3',
    'binary_sensor.ps4': 'PS4',
    'media_player.bio': 'Media Player',
    'binary_sensor.dummy': 'AUX1'
}

if entity_id not in device_source_map:
    logger.error('%s not in device source map', entity_id)
else:
    hass.services.call('media_player', 'select_source',
        {
            'entity_id': 'media_player.denon_3300',
            'source': device_source_map[entity_id]
        }
    )
