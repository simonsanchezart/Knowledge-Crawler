import requests
import json
import os

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

wiki_articles, wiki_in_links = [], []
def search_wikipedia():
    global search_term

    if is_strict():
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&limit=500&search=\"{search_term}\""
    else:
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&limit=500&search={search_term}"
    r = requests.get(url)
    print(f"Wikipedia connection: {r.status_code}")
    if r.status_code != 200:
        print("Not able to use connect to Wikipedia\n")
    else:
        contents = r.json()
        for article in range(len(contents[1])):
            name = contents[1][article]
            link = contents[3][article]
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

            wiki_in_links.append(internal_link_list)
            wiki_articles.append(full_article)


wiki_confirm = check_confirmation(input("Do you want to search the Wikipedia? (y/n) "))
if wiki_confirm:
    search_wikipedia()

youtube_videos, youtube_thumbnails = [], []
def youtube_search(api_key):
    global search_term

    if is_strict():
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&q=\"{search_term}\"&relevanceLanguage=en&type=video&key={api_key}"
    else:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&q={search_term}&relevanceLanguage=en&type=video&key={api_key}"

    r = requests.get(url)
    contents = r.json()
    print(f"Youtube connection: {r.status_code}")
    if r.status_code != 200:
        print("Not able to use connect to Youtube\n")
    else:
        with open("google_api.txt", "w") as f:
            f.write(api_key)
        videos = contents["items"]
        for video in videos:
            name = video["snippet"]["title"]
            id = video["id"]["videoId"]
            video_link = f"<b><a href='https://www.youtube.com/watch?v={id}' target='_blank'>{name}</a></b>"
            thumbnail_image = f"""<img src='{video["snippet"]["thumbnails"]["high"]["url"]}'></img>'"""
            youtube_thumbnails.append(thumbnail_image)
            youtube_videos.append(video_link)


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
        print(f"\nTo use the Youtube and google services you need an API key.")
        has_api = check_confirmation(input("Do you have an API key? (y/n) "))
        if has_api:
            api_key = input("Input your API key: ")
            youtube_search(api_key)
        else:
            print("You can follow these steps to get your API key: "
                  "https://developers.google.com/youtube/v3/getting-started"
                  " Youtube and Google services won't be used.")

if youtube_confirm:
    write_youtube_thumbnails = check_confirmation(input("Do you want to include Youtube thumbnail? (y/n) "))

def write_file():
    file_name = f"information_about_{search_term}.html"
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


write_file()

# print(len(wiki_articles))
# print(wiki_in_links)