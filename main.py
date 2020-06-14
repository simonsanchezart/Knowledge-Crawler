import requests
import json
import os
import pdfkit
from pytube import YouTube
from random import randrange

def check_confirmation(input_text):
    available_anwers = ("yes", "y", "yey")
    if input_text in available_anwers:
        return True
    else:
        return False


def is_strict():
    strict_confirmation = input("Do you want to perform a strict search? (y/n) ")
    return check_confirmation(strict_confirmation)


search_term = input("What do you wanna search for? ")

if not os.path.exists(f"{search_term}"):
    os.mkdir(f"{search_term}")


raw_articles, wiki_articles, wiki_in_links = [], [], []
def search_wikipedia():
    global search_term

    if is_strict():
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&limit=500&search=\"{search_term}\""
    else:
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&limit=500&search={search_term}"
    r = requests.get(url)
    print(f"Wikipedia connection: {r.status_code}")
    if r.status_code != 200:
        print(f"Not able to use connect to Wikipedia {r.status_code}\n")
    else:
        contents = r.json()
        for article in range(len(contents[1])):
            name = contents[1][article]
            link = contents[3][article]
            name_and_link = {"name": name, "link": link}
            full_article = f"<b><a href='{link}' target='_blank'>{name}</a></b>"

            url_links = f"https://en.wikipedia.org/w/api.php?action=query&prop=links&titles={name}&format=json"
            print(f"Getting links for wikipedia article: {name}")
            re = requests.get(url_links)
            contents_links = re.json()
            article_id = list(contents_links["query"]["pages"])[0]
            links = contents_links["query"]["pages"][article_id]["links"]
            internal_link_list = []
            for link in links:
                article_link = f"https://en.wikipedia.org/wiki/{link['title']}"
                full_link = f"<b><a href='{article_link}' target='_blank''>{link['title']} </a></b>"
                internal_link_list.append(full_link)

            raw_articles.append(name_and_link)
            wiki_in_links.append(internal_link_list)
            wiki_articles.append(full_article)


wiki_confirm = check_confirmation(input("Do you want to search the Wikipedia? (y/n) "))
def download_wikipedia():
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    options = {'quiet': ''}

    try:
        articles_quantity = int(input(f"How many articles do you want to download? (max: {len(raw_articles)}) "))
    except ValueError:
        pass
    else:
        if 0 > articles_quantity > len(raw_articles):
            print(f"Input must be integer between 1 and {len(raw_articles)}")
            download_wikipedia()

    articles_to_download = raw_articles[:articles_quantity]
    for article in articles_to_download:
        print(f"Downloading {article['name']} as .pdf")
        pdfkit.from_url(article["link"], f"{search_term}/{article['name']}.pdf", configuration=config, options=options)


if wiki_confirm:
    search_wikipedia()
    confirm_wiki_download = check_confirmation(input("Do you want to convert Wikipedia articles to pdf? (y/n) "))
    if confirm_wiki_download:

        print("\nWARNING: Downloading articles from Wikipedia can be slow ,"
              "if possible, keep the number of articles to download to a minimum.")
        download_wikipedia()


videos_links, youtube_videos, youtube_thumbnails = [], [], []
def youtube_search(api_key):
    global search_term

    if is_strict():
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&q=\"{search_term}\"&relevanceLanguage=en&type=video&key={api_key}"
    else:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&q={search_term}&relevanceLanguage=en&type=video&key={api_key}"

    r = requests.get(url)

    print(f"Youtube connection: {r.status_code}")
    if r.status_code != 200:
        print(f"Not able to use connect to Youtube: {r.status_code}\n")
    else:
        contents = r.json()
        with open("google_api.txt", "w") as f:
            f.write(api_key)
        videos = contents["items"]
        for video in videos:
            name = video["snippet"]["title"]
            id = video["id"]["videoId"]
            video_link = f"https://www.youtube.com/watch?v={id}"
            formatted_video_link = f"<b><a href='{video_link}' target='_blank'>{name}</a></b>"
            thumbnail_image = f"""<img src='{video["snippet"]["thumbnails"]["high"]["url"]}'></img>'"""

            videos_links.append(video_link)
            youtube_thumbnails.append(thumbnail_image)
            youtube_videos.append(formatted_video_link)


youtube_confirm = check_confirmation(input("Do you want to search for Youtube? (y/n) "))
if youtube_confirm:
    filename = "google_api.txt"
    use_prev = False
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            prev_api = f.read()
        use_prev = check_confirmation(input(f"A previous API key ({prev_api}) "
                                            f"has been detected, do you want to use this key? (y/n) "))
    if use_prev:
        youtube_search(prev_api)
    else:
        print(f"\nTo use the Youtube and Google services you need an API key.")
        has_api = check_confirmation(input("Do you have an API key? (y/n) "))
        if has_api:
            api_key = input("Input your API key: ")
            youtube_search(api_key)
        else:
            print("You can follow these steps to get your API key: "
                  "https://developers.google.com/youtube/v3/getting-started"
                  " Youtube and Google services won't be used.")

incrementer = 0
google_posts = []
def google_search(api_key):
    global search_term, incrementer
    start = (incrementer * 10) + 1
    if start > 100:
        start = 100

    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=008211583063684876305:ztaertslmc4&start={start}&q={search_term}"

    r = requests.get(url)
    if incrementer < 1:
        print(f"Google connection: {r.status_code}")
    if r.status_code is not 200 and incrementer < 1:
        print(f"Not able to use connect to Google {r.status_code}\n")
    else:
        contents = r.json()
        links = contents["items"]
        for link in links:
            link_title = link["htmlTitle"]
            link_display_url = link["displayLink"]
            link_url = link["link"]
            link_snippet = link["htmlSnippet"]
            post = {"link_title": link_title, "link_display_url": link_display_url, "link_url": link_url,
                    "link_snippet": link_snippet}
            google_posts.append(post)

    incrementer += 1


google_confirm = check_confirmation(input("Do you want to search in Google? (y/n) "))

pages_to_search = 0
def get_pages_to_search():
    global pages_to_search
    try:
        pages_to_search = int(input("How many pages do you want to search? (1-10) "))
    except ValueError:
        print("Value should be a number between 1 and 10 (inclusive)")
        get_pages_to_search()
    else:
        pages_to_search = max(1, min(pages_to_search, 10))


if google_confirm:
    filename = "google_api.txt"
    use_prev = False
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            prev_api = f.read()
        use_prev = check_confirmation(input(f"A previous API key ({prev_api}) "
                                            f"has been detected, to use this API you will need to "
                                            f"add the Custom Search service to it:\n\n"
                                            f"1- Go to: https://developers.google.com/custom-search/v1/overview"
                                            f"#api_key\n"
                                            f"2- Click 'Get a Key' and select your previously created "
                                            f"project for Youtube search\n"
                                            f"3- This will add the service to that project, then you can use your key."
                                            f"\n\nDo you want to use this key? (y/n) "))

    get_pages_to_search()
    if use_prev:
        for i in range(pages_to_search):
            google_search(prev_api)
    else:
        print(f"\nTo use the Youtube and Google services you need an API key.")
        has_api = check_confirmation(input("Do you have an API key? (y/n) "))
        if has_api:
            api_key = input("Input your API key: ")
            for i in range(pages_to_search):
                google_search(api_key)
        else:
            print("You can follow these steps to get your API key: "
                  "https://developers.google.com/custom-search/v1/overview "
                  "Youtube and Google services won't be used.")

if youtube_confirm:
    write_youtube_thumbnails = check_confirmation(input("Do you want to include Youtube thumbnails? (y/n) "))

def write_file():
    file_name = f"{search_term}/Information about {search_term}.html"
    with open(file_name, "w", encoding='utf-8-sig', ) as f:
        if wiki_confirm:
            f.write(f"<h2>Wikipedia</h2>")
            for article in enumerate(wiki_articles):
                f.write(f"{article[1]}")
                f.write(f"<ul>")
                for link in wiki_in_links[article[0]]:
                    f.write(f"<li>{link}</li>")
                f.write(f"</ul><br >")

        if youtube_confirm:
            f.write(f"<h2>Youtube</h2>")
            for video in range(len(youtube_videos)):
                f.write(f"{youtube_videos[video]}<br >")
                if write_youtube_thumbnails:
                    f.write(f"{youtube_thumbnails[video]}<br >")

        if google_confirm:
            f.write(f"<h2>Google</h2>")
            for post in google_posts:
                f.write(f"<a href='{post['link_url']}' target='_blank'>{post['link_title']} - {post['link_display_url']}</a><br >")
                f.write(f"{post['link_snippet']}<br ><br >")


write_file()

if youtube_confirm:
    confirm_youtube_download = check_confirmation(input("Do you want to download the youtube videos? (y/n) "))

video_quantity = 0
def get_video_quantity():
    global video_quantity
    try:
        print("\nWARNING: Downloading and retrieving data from Youtube can be really slow, "
              "if possible, keep the number of videos to download to a minimum.")
        video_quantity = int(input("\nHow many videos do you want to download? (max: 50) "))
    except ValueError:
        print(f"Input must be a number between 1 and 50 (inclusive)")
        get_video_quantity()
    else:
        video_quantity = max(1, min(video_quantity, 50))

video_quality = 0
def get_video_quality():
    global video_quality
    video_quality = int(input("Choose a quality to download the video (0-2):\n"
                              "0- Highest\n"
                              "1- Mid\n"
                              "2- Lowest\n\n"))
    if 0 > video_quality > 2:
        print("Video quality should be a number between 0 and 2 (inclusive)")
        get_video_quality()


total_size = 0
def download_youtube():
    global total_size
    get_video_quantity()
    get_video_quality()
    videos_to_download = videos_links[:video_quantity]

    print("Getting the total size...")
    for i, video in enumerate(videos_to_download):
        try:
            print(f"Getting size from video {i+1} of {len(videos_to_download)}")
            yt = YouTube(video)
            streams_list = yt.streams.filter(progressive=True).order_by("resolution").desc()
            if video_quality is 0:
                my_stream = streams_list[0]
            elif video_quality is 1:
                index = len(streams_list) // 2
                my_stream = streams_list[index]
            else:
                my_stream = streams_list[-1]
            file_size = my_stream.filesize / 1000000
        except:
            pass
        else:
            total_size += file_size
    proceed = check_confirmation(input(f"\nYou're about to download {round(total_size)} mb in videos,"
                                       f" do you want to proceed? (y/n) "))

    if not proceed:
        total_size = 0
        download_youtube()

    for video in videos_to_download:
        yt = YouTube(video)
        print(f"\nGetting data from \"{yt.title}\"")
        streams_list = yt.streams.filter(progressive=True).order_by("resolution").desc()
        if video_quality is 0:
            my_stream = streams_list[0]
        elif video_quality is 1:
            index = len(streams_list) // 2
            my_stream = streams_list[index]
        else:
            my_stream = streams_list[-1]
        file_size = my_stream.filesize / 1000000
        print(f"\tDownloading {round(file_size)} mb...")
        identifier = randrange(0, 999999999)
        my_stream.download(output_path=f"{search_term}/", filename=f"{yt.title}_{identifier}")


if youtube_confirm and confirm_youtube_download:
    download_youtube()