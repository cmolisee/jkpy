from __future__ import annotations
from typing import Set
from jkpy.handlers.handler import Handler
from jkpy.utils import Ansi
from jkpy.mvc.menu import MenuModel
from jkpy.mvc.menu import MenuView
import httpx
import asyncio
from jkpy.utils import ProgressBar
import sys

class RequestAccountsHandler(Handler):
    def process(self, model: MenuModel, view: MenuView) -> None:
        title="Collecting Jira account data >"
        print(title + view.line_break()[len(title):])
        
        cached=["-".join(dict(account)["displayName"]) for account in model.data["accounts"]]
        accounts_to_get: Set[str]=set(model.data["members"])-set(cached)
        
        for userDisplayName in accounts_to_get:
            account=asyncio.run(self.async_request(userDisplayName, model, view))
            if account:
                model.data["accounts"].add(tuple(account))
        
        print(Ansi.GREEN+"Collected all account data  ✅"+Ansi.RESET)
    
    async def async_request(self, displayName: str, model: MenuModel, view: MenuView):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        async with httpx.AsyncClient(
            base_url=model.data["host"], 
            headers=headers,
            timeout=httpx.Timeout(
                connect=10.0, # time to establish connection
                read=60.0, # time to wait for response data — increase if Jira is slow
                write=10.0, # time to send request body
                pool=10.0, # time to wait for a connection from the pool
            )) as client:
                txt=f">>> [Account Request {displayName}]... "

                sys.stdout.write(txt)
                response = await ProgressBar(min(40, view._width()), len(txt)).run_with(
                    client.get(
                        url=f"/rest/api/3/user/search?query={displayName}", 
                        auth=httpx.BasicAuth(model.data["email"], model.data["token"])
                    )
                )

                response.raise_for_status()
                return response.json()[0]