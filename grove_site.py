from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import soundcloud
from requests import HTTPError
from werkzeug.utils import redirect
from peewee import *


SCID = open('SOUNDCLOUDID', 'r').read()
client = soundcloud.Client(client_id=SCID)


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
    songs = get_songs()
    total_elements = len(songs)  # TODO: count the rows in the db instead of this
    first_item_on_page = 9*(page_number-1)

    return render_template('index.html',
                           ROW1=render_row(songs[first_item_on_page:first_item_on_page+3]),
                           ROW2=render_row(songs[first_item_on_page+3:first_item_on_page+6]),
                           ROW3=render_row(songs[first_item_on_page+6:first_item_on_page+9]),
                           PAGER=render_pager(page_number, total_elements))

    # we need to get up to 9 entries for whichever page_number this is, and populate the rows with up to 3 entries each
    # first_index = (page_number - 1) * 9
    # last_index = first_index + 9
    # if last_index > total_elements:
    #     last_index = total_elements
    #
    # links_cleaned = clean_links(songs[first_index:last_index])
    # while links_cleaned > 0:
    #     links_cleaned = clean_links(songs)

#    cur_songs = songs[first_index:last_index]
    # return render_template('index.html', ROW1=render_row(cur_songs[:3]),
    #                        ROW2=render_row(cur_songs[3:6]), ROW3=render_row(cur_songs[6:]),
    #                        PAGER=render_pager(page_number, total_elements))


def get_songs():
    links = Link.select()
    songs = []
    for link in links:
        songs.append(link.link)
    songs.reverse()
    return songs


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
            pass
            #elements.append(render_vimeo(link))
        else:
            pass  # skip any other links
    return render_template('row.html', elements=elements)


def render_pager(curpage, total_elements):
    if curpage == 1:
        newer_link = "#"
        newer_disabled = " disabled"
        if total_elements > 9:
            older_disabled = ""
            older_link = "/pages/" + str(curpage + 1)
        else:
            older_disabled = " disabled"
            older_link = "#"
    else:
        newer_link = "/pages/" + str(curpage - 1)
        newer_disabled = ""
        if total_elements > curpage * 9:
            older_disabled = ""
            older_link = "/pages/" + str(curpage + 1)
        else:
            older_disabled = " disabled"
            older_link = "#"
    return render_template("pager.html", DISABLED1=older_disabled, DISABLED2=newer_disabled, OLDER=older_link, NEWER=newer_link)


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
        if "?" in uri:
            uri = uri.split("?")[0]
    else:
        uri = url.split("=")[-1]

    return render_template("youtube.html", URI=uri)


# verify that a soundcloud link works because the API bars some songs from displaying & we don't want this to crash us
def verify_soundcloud(url):
    try:
        if "/sets/" in url:
            print("THIS ISN'T SUPPORTED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")  # TODO: this is gross
            raise HTTPError
        track = client.get('/resolve', url=url)
    except HTTPError:
        # The soundcloud API will randomly fail on some tracks for no apparent reason
        # see: http://stackoverflow.com/questions/36360202/soundcloud-api-urls-timing-out-and-then-returning-error-403-on-about-50-of-trac
        return False
    return True


def render_soundcloud(url):
    # render a soundcloud embed
    if "/sets/" in url:
        print("THIS ISN'T SUPPORTED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")  # TODO: this is gross
    try:
        track = client.get('/resolve', url=url)
    except HTTPError:
        # The soundcloud API will randomly fail on some tracks for no apparent reason
        # see: http://stackoverflow.com/questions/36360202/soundcloud-api-urls-timing-out-and-then-returning-error-403-on-about-50-of-trac
        pass
    return render_template("soundcloud.html", URI=track.id)


def clean_links(links):
    links_cleaned = 0
    for link in links:
        if 'soundcloud' in link:
            is_valid_link = verify_soundcloud(link)
            if not is_valid_link:
                links_cleaned += 1
                links.remove(link)
    return links_cleaned


class Link(Model):
    user = CharField()
    message = TextField()
    time = DateTimeField()
    link = TextField()

    class Meta:
        database = db


if __name__ == "__main__":
    app.run()
