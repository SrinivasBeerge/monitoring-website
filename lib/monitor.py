import asyncio
import json
import time
from typing import List
import re

import aiohttp

from lib.kafka import Producer


class Monitor:
    def __init__(self, config: dict):
        self.interval = config['monitor_interval']
        self.producer = Producer(
                config['kafka']['server'],
                config['kafka']['topic']
        )

    async def monitor_and_produce(self, websites: List[str]):
        '''
        Method to monitor website asynchronously
        '''

        print(f'Monitoring sites {websites}')
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
            while True:
                start = time.time()
                tasks = []
                for site in websites:
                    tasks.append(self._get_website(session, site))
                await asyncio.gather(*tasks)

                end_time = time.time() - start
                sleep_time = max(0, int(self.interval - end_time))
                print(
                        'Producer: Queried %d sites in %.2f seconds. '
                        'Sleeping for %d seconds...' %
                        (len(websites), end_time, sleep_time)
                )
                time.sleep(sleep_time)

    async def _get_website(self, session: aiohttp.ClientSession, site_url: str):
        '''
        Method to produce stats to Kafka.
        '''

        start = time.time()
        response = await session.get(site_url)
        # Since every website has its own url in it
        # using regex searching if we are on the right site
        resp_body = await response.text()
        regex_exp = re.compile(str(site_url))
        regex_finds = regex_exp.search(resp_body)
        if regex_finds:
            print ("Regex matched site is %s"%site_url)
        end = int((time.time() - start) * 1000)
        print(f'Producer: {site_url} returned {response.status}')
        # TODO: Handle timeouts and log accordingly

        message = {
            'site_url': site_url,
            'http_status': response.status,
            'response_time': end
        }
        self.producer.produce(json.dumps(message).encode('utf-8'))
