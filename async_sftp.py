#!/usr/bin/python3

import asyncio
import asyncssh
import yaml

"""
host.yml format
hostname1:
  username: admin
  ip: 1.1.1.1
  password: 1234
hostname2:
  username: ivan
  ip: 1.1.1.2
  password: 12345
...
"""
with open('hosts.yml') as f:
    devices = yaml.safe_load(f)

devs = []
failed_to_connect = []

for ne, params in devices.items():
    device = {'username': params['username'],
              'password': params['password'],
              'host': params['ip'],
              'known_hosts': None,
              }
    devs.append({ne: device})


async def run_client(host, param):
    try:
        async with asyncssh.connect(**param) as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.mput('/path_somedir/*')
                print(f'Files have been copied to {host}')
    except:
        failed_to_connect.append(host)


async def run():
    tasks = [
        loop.create_task(run_client(*param.keys(), *param.values()))
        for param in devs
    ]
    await asyncio.wait(tasks)


loop = asyncio.get_event_loop()
loop.run_until_complete(run())

if len(failed_to_connect) > 0:
    failed_to_connect = '\n'.join(list(set(failed_to_connect)))
    print(f"Failed to connect:\n{failed_to_connect}")
