
import sys
import httpx
import time
import random

target = 'http://165.227.185.117:8000'
token = 'helixflow-token'

def send(model, prompt, project):
    url = f'{target}/v1/chat/completions'
    headers = {'Authorization': f'Bearer {token}', 'X-Project': project}
    payload = {'model': model, 'messages': [{'role': 'user', 'content': prompt}]}
    try:
        httpx.post(url, json=payload, headers=headers, timeout=10.0)
    except Exception as e:
        pass

for i in range(15):
    send('deepseek-chat', 'Hello ' * random.randint(1, 10), 'project-alpha')
    send('auto', 'Hello ' * random.randint(1, 10), 'project-beta')
    time.sleep(0.5)

