from __future__ import annotations

import asyncio
import sys
from typing import Any

import httpx
import polars as pl

from jkpy.handlers.handler import Handler
from jkpy.mvc.menu import MenuModel, MenuView
from jkpy.utils import Ansi, ProgressBar


class RequestIssues(Handler):
    """Fetch all the raw data (issues)"""

    def process(self, model: MenuModel, view: MenuView) -> None:
        title = "Collecting Jira issues >"
        print(title + view.line_break()[len(title) :])

        query: str = self.get_jql_query(model)

        all_issues = asyncio.run(self.async_request(query, model, view))
        print(Ansi.GREEN + f"Collected {len(all_issues)} total issues  ✅\n" + Ansi.RESET)

        model.data["df_issues"] = pl.json_normalize(all_issues, infer_schema_length=None)
        model.data["raw_issues"] = all_issues

    def get_jql_query(self, model: MenuModel) -> str:
        jql_parts: list[str] = ["("]
        # labels or teams
        members = [f"'{label}'" for label in model.data["members"]]
        jql_parts.append(f"(labels in ({','.join(members)}))")
        jql_parts.append(" OR ")
        teams = [f"'{team}'" for team in model.data["teams"]]
        jql_parts.append(f"('Team Name[Dropdown]' in ({','.join(teams)})))")
        # labels to ignore
        if len(model.data["ignore_labels"]) >= 1:
            jql_parts.append(" AND ")
            labels_to_ignore = [f"'{label}'" for label in model.data["ignore_labels"]]
            jql_parts.append(f" labels not in ({','.join(labels_to_ignore)})")
        # ticket types
        jql_parts.append(" AND ")
        jql_parts.append("type in (Story, Task, Bug, Enhancement)")
        # statuses
        jql_parts.append(" AND ")
        statuses = [f"'{status}'" for status in model.data["statuses"]]
        jql_parts.append(f"status CHANGED TO ({','.join(statuses)})")
        # time range
        jql_parts.append(
            f" AFTER {model.data['start'].strftime('%Y-%m-%d')} BEFORE {model.data['end'].strftime('%Y-%m-%d')}"
        )

        jql = "".join(jql_parts)
        print(">>> Building JQL...")
        print()
        print(Ansi.CYAN + jql + Ansi.RESET)
        print()

        return jql

    async def async_request(self, query: str, model: MenuModel, view: MenuView) -> list[Any]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        all_issues = []
        next_page_token: str | None = None
        page = 1

        async with httpx.AsyncClient(
            base_url=model.data["host"],
            headers=headers,
            timeout=httpx.Timeout(
                connect=10.0,  # time to establish connection
                read=60.0,  # time to wait for response data — increase if Jira is slow
                write=10.0,  # time to send request body
                pool=10.0,  # time to wait for a connection from the pool
            ),
            verify=False,
        ) as client:
            while True:
                txt = f">>> [Issue Request {page}]... "
                payload = {
                    "jql": query,
                    "maxResults": 150,
                    "fields": [
                        "key",
                        "summary",
                        "labels",
                        "timespent",
                        "customfield_10264",
                        "customfield_10235",
                        "customfield_10028",
                    ],
                    "expand": "changelog",
                    **({"nextPageToken": next_page_token} if next_page_token else {}),
                }

                sys.stdout.write(txt)
                response = await ProgressBar(min(40, view._width()), len(txt)).run_with(
                    client.post(
                        url="/rest/api/3/search/jql",
                        auth=httpx.BasicAuth(model.data["email"], model.data["token"]),
                        json=payload,
                    )
                )

                response.raise_for_status()
                body = response.json()

                issues = body.get("issues", [])
                all_issues.extend(issues)

                next_page_token = body.get("nextPageToken")
                page += 1
                if not next_page_token:
                    break
            return all_issues
