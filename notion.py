import os
from urllib.parse import urlparse

import tmdb
import notion_client
from notion_client import helpers


notion = notion_client.Client(
    auth=os.environ["NOTION_MARKER_NOTION_TOKEN"],
)


def get_movie_database(database_id: str):
    return helpers.iterate_paginated_api(
        notion.databases.query,
        database_id=database_id,
    )


def notion_title(s):
    return {"title": [{"type": "text", "text": {"content": s}}]}


def notion_rich_text(s):
    return {"rich_text": [{"type": "text", "text": {"content": s}}]}


def notion_date(s):
    return {"date": {"start": s}}


def notion_select(s):
    return {"select": {"name": s}}


def notion_multi_select(enums):
    return {"multi_select": [{"name": e} for e in enums]}


def notion_url(url):
    return {"url": url}


def notion_file(url):
    return {
        "files": [
            {
                "type": "external",
                "name": os.path.split(urlparse(url).path)[-1],
                "external": {"url": url},
            }
        ]
    }


def update_video_database():
    database_id = os.environ["NOTION_MARKER_NOTION_MOVIE_DATABASE_ID"]
    for block in get_movie_database(database_id):
        page = block[0]
        for page in block:
            row = page["properties"]
            tmdb_url = row["tmdb链接"]["url"]
            data_status = row["数据状态"]["select"]
            if data_status is not None:
                data_status = data_status["name"]
            if tmdb_url is not None and tmdb_url != "" and data_status != "已更新":
                row_to_update = dict()
                info = tmdb.get_media_info(tmdb_url)
                row_to_update["tmdb_id"] = notion_title(info.tmdb_id)
                row_to_update["名称"] = notion_rich_text(info.name)
                row_to_update["发行日期"] = notion_date(info.release_date)
                row_to_update["分类"] = notion_multi_select(info.genres)
                row_to_update["简介"] = notion_rich_text(info.overview)
                row_to_update["封面"] = notion_file(info.poster_url)
                row_to_update["媒体类型"] = notion_select(info.media_type)
                row_to_update["国家/地区"] = notion_multi_select(info.countries)
                row_to_update["imdb链接"] = notion_url(info.imdb_url)
                row_to_update["数据状态"] = notion_select("已更新")
                notion.pages.update(page["id"], **{"properties": row_to_update})
