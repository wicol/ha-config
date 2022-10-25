import datetime
import pytz

import hassapi as hass

class TelegramCommands(hass.Hass):
    def initialize(self):
        self.listen_event(self.handle_command_event, 'telegram_command')
    
    def handle_command_event(self, event, event_data, kwargs):
        command = event_data['command'].split('@')[0].lstrip('/')
        handler = getattr(self, f'handle_{command}', None)
        if not handler:
            self.log(f'No handler for command "{command}"')
            return
        
        self.log(f'Handling {command}')
        handler(event_data)

    def send_message(self, chat_id, message):
            self.call_service(
                'telegram_bot/send_message',
                target=chat_id,
                message=message
            )
    
    def handle_garage(self, event_data): 
        if self.get_state('input_boolean.telegram_command_garage_door') == 'on':
            self.call_service('shell_command/garage_door')
            self.send_message(event_data['chat_id'], 'Garage triggered')
        else:
            self.send_message(event_data['chat_id'], 'Garage door control is disabled')

    def handle_garage2(self, event_data): 
        if self.get_state('input_boolean.telegram_command_garage_door') == 'on':
            self.call_service('shell_command/garage_door')
            self.send_message(event_data['chat_id'], 'Garage triggered')
        else:
            self.send_message(event_data['chat_id'], 'Garage door control is disabled - requesting unlock...')
            self.notify(
                message='Telegram - Garage door requested but its LOCKED YO',
                name='mobile_app_s21',
                data={
                    'tag': 'garage-telegram-request',
                    'actions': [
                        {'title': 'Unlock', 'action': 'garage_enable_telegram_integration'}, 
                        {'title': 'Open', 'action': 'garage_door_trigger'}
                    ]
                }
            )

    def handle_test(self, event_data):
        self.log(f'handle_test: {event_data}')
        self.log(f'command args: {event_data["args"]}')
