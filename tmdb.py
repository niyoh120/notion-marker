import os
import typing as t
from urllib.parse import urlparse
import gettext

import pycountry
from tmdbv3api import TMDb, Movie, TV
import pydantic

tmdb = TMDb()
tmdb.api_key = os.environ["NOTION_MARKER_TMDB_API_KEY"]

tmdb.language = "zh"

movie = Movie()
tv = TV()


TMDB_MEDIA_TYPE = {"movie": "电影", "tv": "电视剧"}

chinese = gettext.translation("iso3166-1", pycountry.LOCALES_DIR, languages=["zh"])
chinese.install()


def get_imdb_url(title: str) -> t.Optional[str]:
    if title is None or title == "":
        return None
    return "https://www.imdb.com/title/" + title + "/"


def get_detail_finder(media_type):
    return {
        "movie": movie,
        "tv": tv,
    }[media_type]


def get_poster_url(detail) -> str:
    return "https://image.tmdb.org/t/p/w500" + detail["poster_path"]


class MediaInfo(pydantic.BaseModel):
    name: str = ""
    tmdb_id: str = ""
    release_date: str = ""
    genres: t.List[str] = []
    overview: str = ""
    poster_url: str = ""
    imdb_url: t.Optional[str] = None
    media_type: str = ""
    countries: t.List[str] = []


def get_media_info(url: str):
    paths = urlparse(url.removesuffix("/")).path.split("/")
    media_type, tmdb_id = paths[-2], paths[-1]
    if media_type not in TMDB_MEDIA_TYPE:
        raise RuntimeError(f"Unsupported media type {media_type}")
    detail = get_detail_finder(media_type).details(tmdb_id)
    media = MediaInfo()

    media.tmdb_id = tmdb_id
    media.media_type = media_type
    media.genres = [x["name"] for x in detail["genres"]]
    media.overview = detail["overview"]
    media.poster_url = get_poster_url(detail)
    media.media_type = TMDB_MEDIA_TYPE[media_type]
    media.countries = [chinese.gettext(x["name"]) for x in detail["production_countries"]]

    if media_type == "movie":
        media.name = detail["title"]
        media.release_date = detail["release_date"]
    else:
        media.name = detail["name"]
        media.release_date = detail["first_air_date"]
    if "imdb_id" in detail:
        media.imdb_url = get_imdb_url(detail["imdb_id"])
    return media
