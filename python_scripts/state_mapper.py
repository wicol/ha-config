entity_id = data['entity_id']
entity_state = data['state']
state_map = data['state_map']
defaults = {
    'state': 'on',
    'match_service': 'homeassistant.turn_on',
    'nomatch_service': 'homeassistant.turn_off'
}

#state_map:
#  <source_entity_id>:
#    state: 'on'
#    target: <some_entity_id>
#    match_service: homeassistant.turn_on
#    nomatch_service: homeassistant.turn_off

if entity_id not in state_map:
    logger.error('%s not in state_map', entity_id)
    exit(1)

entity_state_map = {**defaults, **state_map[entity_id]}
service_type = 'match_service' if entity_state == entity_state_map['state'] else 'nomatch_service'
domain, service = entity_state_map[service_type].split('.')

logger.debug('%s, %s, %s, service_type: %s', entity_id, entity_state, entity_state_map, service_type)
logger.info('%s -> %s. %s.%s -> %s', entity_id, entity_state, domain, service, entity_state_map['target'])

hass.services.call(domain, service, {'entity_id': entity_state_map['target']})
