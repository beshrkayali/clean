# Copyright (c) 2021 Beshr Kayali

# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.

# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:

# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

import asyncio

import aiohttp
from newspaper import Article
from sanic import Sanic, response

app = Sanic(__name__)

INDEX = """<!DOCTYPE html>
<title>Clean</title>
<h2>Clean</h2>
<p>A JSON API that wraps <a href="https://pypi.org/project/newspaper3k/">newspaper3k</a> to scrape one or more article urls.</a>

<form action="/" method="get">
<span>Try it:</span><br/>
<input name="url" /> <input type="submit" />
</form>
<ul>
    <li><a href="/?url=https://www.atlasobscura.com/articles/pointing-and-calling-japan-trains">/?url=https://www.atlasobscura.com/articles/pointing-and-calling-japan-trains</a>
    <li><a href="/?url=https://en.wikipedia.org/wiki/Data_scraping">/?url=https://en.wikipedia.org/wiki/Data_scraping</a>
    <li><a href="/?url=https://daringfireball.net/2009/04/complex&url=https://daringfireball.net/2020/07/new_york_times_refer_this_dickbar">/?url=https://daringfireball.net/2009/04/complex&url=https://daringfireball.net/2020/07/new_york_times_refer_this_dickbar</a>
</ul>
<p>Source code: <a href="https://github.com/beshrkayali/clean">github.com/beshrkayali/clean</a></p>
"""


async def parse(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                article = Article(url)
                html = await response.text()
                article.download(input_html=html)
                article.parse()

                return {
                    "ok": True,
                    "title": article.title,
                    "text": article.text,
                    "top_image": article.top_image,
                    "publish_date": article.publish_date.isoformat()
                    if article.publish_date
                    else None,
                    "authors": article.authors,
                    "url": url,
                }

            return {
                "ok": False,
                "error": f"Got status {response.status}",
                "url": url,
            }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "url": url,
        }


@app.route("/")
async def handle(request):
    urls = request.args.getlist("url")

    if urls:
        if len(urls) > 5:
            return response.json(
                [{"ok": False, "error": "Max 5 URLs allowed"}], status=400
            )

        async with aiohttp.ClientSession() as session:
            data = await asyncio.gather(*[parse(session, url) for url in urls])

            return response.json(
                data,
                headers={"Access-Control-Allow-Origin": "*"},
            )
    else:
        return response.html(INDEX)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8006)
