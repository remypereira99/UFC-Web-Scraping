from pathlib import Path
from scrapy.http import HtmlResponse, Request, TextResponse


def load_html_response_from_file(path: str | Path) -> HtmlResponse:
    with open(path, "rb") as file:
        body = file.read()
        file_name = file.name.split("/")[-1]
        url_suffix = file_name.replace(".html", "")

    url = f"http://www.ufcstats.com/{url_suffix}"
    request = Request(url=url)
    response = HtmlResponse(url=url, request=request, body=body)

    return response


def load_json_response_from_file(path: str | Path) -> TextResponse:
    with open(path, "rb") as file:
        body = file.read()

    url = "https://api.fightodds.io/gql"
    request = Request(url=url)
    response = TextResponse(url=url, request=request, body=body, encoding="utf-8")

    return response
