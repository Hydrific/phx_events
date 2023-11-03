#!/usr/bin/env python3

import asyncio
from concurrent.futures import ThreadPoolExecutor
from logging import DEBUG, Formatter, StreamHandler, getLogger
from inspect import currentframe, getframeinfo
from time import sleep

from phx_events.client import PHXChannelsClient
from phx_events.phx_messages import ChannelMessage, Event, Topic

logger = getLogger()
formatter = Formatter('-%(asctime)s - %(name)s - %(filename)s:%(lineno)d %(funcName)s() - %(levelname)s - %(message)s')
ss = StreamHandler()
ss.setLevel(DEBUG)
ss.setFormatter(formatter)
logger.addHandler(ss)

def print_handler(message: ChannelMessage, client: PHXChannelsClient) -> None:
    client.logger.debug(f'DEFAULT: {message=}')
    

async def async_print_handler(message: ChannelMessage, client: PHXChannelsClient) -> None:
    client.logger.debug(f'ASYNC: {message=}')


async def main() -> None:
    token = 'auth_token'
    client: PHXChannelsClient

    with ThreadPoolExecutor() as pool:
        url = "wss://device.hydrific.me/socket/websocket"
        hl = [print_handler, async_print_handler]
        async with PHXChannelsClient(channel_socket_url=url) as client:
            client.logger.debug("Registering update event")
            client.register_event_handler(event=Event('update'), handlers=hl)
            client.register_event_handler(event=Event('reboot'), handlers=hl)
            client.register_event_handler(event=Event('phx_err'),  handlers=hl)
            client.register_event_handler(event=Event('phx_reply'), handlers=hl)
            client.register_event_handler(event=Event('phx_close'), handlers=hl)
            #client.register_topic_subscription(Topic('console'))
            client.register_topic_subscription(Topic('device'))
            #client.register_topic_subscription(Topic('firmware:dfe35755-96f1-40b6-Bb9a-65c5443ae74e'))
            await client.start_processing(pool)


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
