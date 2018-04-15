from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import soundcloud
from requests import HTTPError
from werkzeug.utils import redirect
from peewee import *


SCID = open('SOUNDCLOUDID', 'r').read().strip()
client = soundcloud.Client(client_id=SCID)
SUPPORTED_LINKS = ["youtu.be", "youtube.com", "spotify.com", "soundcloud.com"]
LINKS_PER_PAGE = 9


def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    return app


app = create_app()
db = SqliteDatabase('grovedb')
db.connect()


@app.route("/")
def render_home():
    # redirect from the homepage to the first page
    return redirect("/pages/1")


@app.route("/pages/<int:page_number>")
def render_index(page_number):
    if page_number <= 0:
        return redirect("/pages/1")

    songs = get_songs()
    total_elements = len(songs)
    first_item_on_page = LINKS_PER_PAGE*(page_number-1)

    return render_template('index.html',
                           ROW1=render_row(songs[first_item_on_page:first_item_on_page+3]),
                           ROW2=render_row(songs[first_item_on_page+3:first_item_on_page+6]),
                           ROW3=render_row(songs[first_item_on_page+6:first_item_on_page+9]),
                           PAGER=render_pager(page_number, total_elements))


def get_songs():
    links = Link.select()
    songs = []
    for link in links:
        if is_supported(link.link):
            songs.append(link.link)
    songs.reverse()
    return songs


def is_supported(link):
    for url in SUPPORTED_LINKS:
        if "soundcloud" in link and valid_soundcloud_link(link):
            return True
        elif url in link:
            return True
    return False


def render_row(links):
    if len(links) == 0:
        return ""
    elements = []
    for link in links:
        if "spotify" in link:
            elements.append(render_spotify(link))
        elif "youtu" in link:
            elements.append(render_youtube(link))
        elif "soundcloud" in link:
            elements.append(render_soundcloud(link))
        elif "vimeo" in link:
            elements.append(render_vimeo(link))
    return render_template('row.html', elements=elements)


def render_pager(page_number, total_elements):
    can_go_forward = False
    can_go_back = False

    if next_page_exists(page_number, total_elements):
        can_go_forward = True

    if previous_page_exists(page_number):
        can_go_back = True

    return render_template("pager.html", page_number=page_number, can_go_back=can_go_back, can_go_forward=can_go_forward)


def next_page_exists(page_number, total_elements):
    if total_elements > page_number * LINKS_PER_PAGE:
        return True
    return False


def previous_page_exists(page_number):
    if page_number != 1:
        return True
    return False


def render_spotify(url):
    # render a spotify embed
    if ':' in url:
        uri = url
    else:
        # Convert this URL to a URI
        url = url.split("/")
        uri = "spotify"
        for x in range(3, len(url)):
            uri += ":" + url[x]
    return render_template('spotify.html', URI=uri)


def render_youtube(url):
    # render a youtube embed
    if "youtu.be" in url:
        uri = url.split("/")[-1]
    else:
        uri = url.split("=")[-1]

    return render_template("youtube.html", URI=uri)


def valid_soundcloud_link(url):
    if "soundcloud" in url and "/sets/" in url:  # we can't support sets.
        return False
    return True


def render_soundcloud(url):
    # render a soundcloud embed
    try:
        track = client.get('/resolve', url=url, allow_redirects=False)
    except HTTPError as error:
        print(error)
        return render_template("soundcloud.html", URI=None, error=True, error_text=error)
    return render_template("soundcloud.html", URI=track.location, error=False, error_text="")


def render_vimeo(url):
    uri = url.split("/")[-1]

    return render_template("vimeo.html", URI=uri)


class Link(Model):
    user = CharField()
    message = TextField()
    time = DateTimeField()
    link = TextField()

    class Meta:
        database = db


if __name__ == "__main__":
    app.run(host='0.0.0.0')
