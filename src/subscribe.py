import base64
import os
import subprocess

import uvicorn
import aiohttp
from fastapi import FastAPI
from starlette.responses import HTMLResponse
import schedule
import click


def get_links_from_target(target: str = ''):
    links = []
    for host in hosts:
        #        cmd = "ssh root@" + host + r""" 'v2ray url | grep "vless://" | sed -r "s/[[:cntrl:]]\[[0-9]{1,3}m//g"'"""
        cmd = r'v2ray url | grep "vmess://" | sed -r "s/[[:cntrl:]]\[[0-9]{1,3}m//g"'
        print(cmd)
        link = subprocess.getoutput(cmd)
        links.append(link[link.index('vmess'):-1])
    return links


def change_caddy_https_port():
    """
    new-http-port = old-http-port + 1
    :return:
    """
    https_port = subprocess.getoutput("grep https_port /etc/caddy/Caddyfile | awk '{ print $2 }'")
    replace_port = os.system(f"sed -ie 's/{https_port}/{str(int(https_port) + 1)}/g' /etc/caddy/Caddyfile")




app = FastAPI(
    title="Management API For Automation",
    servers=[
        {"url": 'https://automation-prod.nftgo.io/', "description": "Production environment"},
    ],
    version='v0.0.1',
    description='for automation',
)


@app.get('/')
@app.get('/subscribe')
async def subscribe():
    links = get_links_from_target()
    res = '\n'.join(links)
    html = base64.b64encode(res.encode(encoding='utf8'))
    return HTMLResponse(content=html, status_code=200)


@app.get('/subscribe/clash')
async def subscribe_clash():
    link = 'http://116.62.45.83:9001/subscribe'
    async with aiohttp.ClientSession() as session:
        url = f'http://127.0.0.1:25500/sub?target=clash&url={link}'
        async with session.get(url) as resp:
            text = await resp.text()
    return HTMLResponse(content=text, status_code=200)


@click.command()
@click.option('--port', default=9001)
def start(port: int):
    schedule.every().day.at("10:10").do(change_caddy_https_port)
    uvicorn.run(
        "subscribe:app",
        host='0.0.0.0',
        port=port,
        log_level="info",
    )


if __name__ == '__main__':
    start()
