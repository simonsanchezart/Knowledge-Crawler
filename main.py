from requests import get
from re import compile
from os import path, mkdir
from pdfkit import configuration, from_url
from urllib import request
from pytube import YouTube
from random import randrange

def check_confirmation(input_text):
    available_anwers = ("yes", "y", "yey")
    if input_text in available_anwers:
        return True
    else:
        return False


def format_string(input_text):
    regex = compile('[^a-zA-Z0-9" "]')
    return regex.sub("", input_text)


search_term = input("What do you wanna search for? ")
search_term = format_string(search_term)

if not path.exists(f"{search_term}"):
    mkdir(f"{search_term}")


raw_articles, wiki_articles, wiki_in_links = [], [], []
def search_wikipedia():
    global search_term

    url = f"https://en.wikipedia.org/w/api.php?action=opensearch&limit=500&search={search_term}"
    r = get(url)
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
            re = get(url_links)
            contents_links = re.json()
            article_id = list(contents_links["query"]["pages"])[0]
            try:
                links = contents_links["query"]["pages"][article_id]["links"]
            except:
                print(f"Wasn't able to get article {name}")
                continue
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
    if path.isfile("wkhtmltopdf_path.txt"):
        wkhtml_folder = open("wkhtmltopdf_path.txt", "r").read()
    else:
        print(f"To convert Wikipedia articles you need to to download wkhtmltopdf: "
              f"https://wkhtmltopdf.org/downloads.html"
              f"\n"
              f"Once you've downloaded it, you will be asked to indicate the folder where wkhtmltopdf.exe is in.\n")

        wkhtml_folder = input("Location of wkhtmltopdf.exe: ")

    config = configuration(wkhtmltopdf=rf"{wkhtml_folder}\\wkhtmltopdf.exe")
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
    if not path.exists(f"{search_term}/Wikipedia"):
        mkdir(f"{search_term}/Wikipedia")
    try:
        for article in articles_to_download:
            print(f"Downloading {article['name']} as .pdf")
            formatted_article_name = format_string(article['name'])
            from_url(article["link"], f"{search_term}/Wikipedia/{formatted_article_name}.pdf",
                     configuration=config, options=options)
    except:
        print(f"Wasn't able to download Wikipedia articles. Check the path of wkhtmltopdf.exe.")
    else:
        with open("wkhtmltopdf_path.txt", "w") as f:
            f.write(wkhtml_folder)


if wiki_confirm:
    search_wikipedia()
    if not wiki_articles:
        print(f"No Wikipedia articles were found")


videos_links, youtube_videos, youtube_thumbnails = [], [], []
def youtube_search(api_key):
    global search_term

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=50&q={search_term}&relevanceLanguage=en&type=video&key={api_key}"

    r = get(url)

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
    if path.isfile(filename):
        with open(filename, "r") as f:
            prev_api = f.read()
        use_prev = check_confirmation(input(f"\nA previous API key ({prev_api}) "
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

    r = get(url)
    if incrementer < 1:
        print(f"Google connection: {r.status_code}")
    if r.status_code is not 200 and incrementer < 1:
        print(f"Not able to use connect to Google {r.status_code}\n")
    else:
        contents = r.json()
        links = contents["items"]
        for link in links:
            try:
                link_title = link["htmlTitle"]
                link_display_url = link["displayLink"]
                link_url = link["link"]
                link_snippet = link["htmlSnippet"]
                post = {"link_title": link_title, "link_display_url": link_display_url, "link_url": link_url,
                        "link_snippet": link_snippet}
            except:
                continue
            else:
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
    if path.isfile(filename):
        with open(filename, "r") as f:
            prev_api = f.read()
        use_prev = check_confirmation(input(f"\nA previous API key ({prev_api}) "
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

incrementer = 0
google_books = []
def book_search(api_key):
    global search_term, incrementer
    start = (incrementer * 10) + 1
    if start > 100:
        start = 100

    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx=008211583063684876305:ztaertslmc4&start={start}&fileType=pdf&q={search_term}%20book"

    r = get(url)
    if incrementer < 1:
        print(f"Google connection: {r.status_code}")
    if r.status_code is not 200 and incrementer < 1:
        print(f"Not able to use connect to Google {r.status_code}\n")
    else:
        contents = r.json()
        links = contents["items"]
        for link in links:
            try:
                link_title = link["title"]
                link_display_url = link["displayLink"]
                link_url = link["link"]
                link_snippet = link["htmlSnippet"]
                book = {"link_title": link_title, "link_display_url": link_display_url, "link_url": link_url,
                        "link_snippet": link_snippet}
            except:
                continue
            else:
                google_books.append(book)

    incrementer += 1


book_search_confirmation = check_confirmation(input("Do you want to search for .pdf books? (y/n) "))

books_to_search = 0
def get_books_to_search():
    global books_to_search
    try:
        books_to_search = int(input("How many books do you want to search for? (1-100) "))
    except ValueError:
        print("Value should be a number between 1 and 100 (inclusive)")
        get_books_to_search()
    else:
        books_to_search = int(books_to_search / 10)
        books_to_search = max(1, min(books_to_search, 10))


if book_search_confirmation:
    filename = "google_api.txt"
    use_prev = False
    if path.isfile(filename):
        with open(filename, "r") as f:
            prev_api = f.read()
        use_prev = check_confirmation(input(f"\nA previous API key ({prev_api}) "
                                            f"has been detected, to use this API you will need to "
                                            f"add the Custom Search service to it:\n\n"
                                            f"1- Go to: https://developers.google.com/custom-search/v1/overview"
                                            f"#api_key\n"
                                            f"2- Click 'Get a Key' and select your previously created "
                                            f"project for Youtube search\n"
                                            f"3- This will add the service to that project, then you can use your key."
                                            f"\n\nDo you want to use this key? (y/n) "))

    get_books_to_search()
    if use_prev:
        for i in range(books_to_search):
            book_search(prev_api)
    else:
        print(f"\nTo download books you need a Google API key.")
        has_api = check_confirmation(input("Do you have an API key? (y/n) "))
        if has_api:
            api_key = input("Input your API key: ")
            for i in range(books_to_search):
                book_search(api_key)
        else:
            print("You can follow these steps to get your API key: "
                  "https://developers.google.com/custom-search/v1/overview "
                  "Youtube and Google services won't be used.")


quantity_of_books_to_download = 0
def get_quantity_of_books_to_download():
    global quantity_of_books_to_download
    try:
        quantity_of_books_to_download = int(input(f"How many books do you want to download? (1-{len(google_books)}) "))
    except ValueError:
        print(f"Input must be a number between 1 and {len(google_books)} (inclusive)")
        get_quantity_of_books_to_download()
    else:
        quantity_of_books_to_download = max(1, min(quantity_of_books_to_download, len(google_books)))


total_books_size = 0
def download_books():
    global quantity_of_books_to_download, total_books_size
    get_quantity_of_books_to_download()
    books_to_download = google_books[:quantity_of_books_to_download]

    for book in books_to_download:
        print(f"Getting size for book \"{book['link_title']}\"...")
        url = book["link_url"]
        try:
            site = request.urlopen(url)
        except:
            print(f"Wasn't able to get book \"{book['link_title']}\"")
            books_to_download.remove(book)
        try:
            total_books_size += site.length
        except TypeError:
            print(f"Wasn't able to get size for book \"{book['link_title']}\"")
    total_books_size = total_books_size / 1000000

    continue_downloading = check_confirmation(input(f"You're about to download about {round(total_books_size, 2)} mb of books, "
                                                    f"do you want to continue? (y/n) "))
    if continue_downloading:
        if not path.exists(f"{search_term}/Books"):
            mkdir(f"{search_term}/Books")
        for book in books_to_download:
            try:

                url = book["link_url"]
                size = request.urlopen(url).length / 1000000
                print(f"Downloading book \"{book['link_title']}\" ({round(size, 2)} mb)...")
                r = get(url)
                identifier = randrange(0, 999999999)
                formatted_book_title = format_string(book['link_title'])
                open(f"{search_term}/Books/{formatted_book_title}_{identifier}.pdf", "wb").write(r.content)
            except:
                print(f"Wasn't able to download \"{book['link_title']}\"")
    else:
        download_books()


if youtube_videos:
    write_youtube_thumbnails = check_confirmation(input("Do you want to include Youtube thumbnails in the file? (y/n) "))

def write_file():
    file_name = f"{search_term}/Information about {search_term}.html"

    with open(file_name, "w", encoding='utf-8-sig', ) as f:
        f.write(f"<h1 id='top'>Sections:</h1>")
        if wiki_articles:
            f.write(f"<a href='#wikipedia'>Wikipedia</a><br >")
        if youtube_videos:
            f.write(f"<a href='#youtube'>Youtube</a><br >")
        if google_posts:
            f.write(f"<a href='#google'>Google</a><br>")
        if google_books:
            f.write(f"<a href='#books'>Books</a><br>")

        if wiki_articles:
            f.write(f"<h2 id='wikipedia'>Wikipedia - <a href='#top'>Goto top</a><br></h2>")
            for article in enumerate(wiki_articles):
                f.write(f"{article[1]}")
                f.write(f"<ul>")
                for link in wiki_in_links[article[0]]:
                    f.write(f"<li>{link}</li>")
                f.write(f"</ul><br >")

        if youtube_videos:
            f.write(f"<h2 id='youtube'>Youtube - <a href='#top'>Goto top</a><br></h2>")
            for video in range(len(youtube_videos)):
                f.write(f"{youtube_videos[video]}<br >")
                if write_youtube_thumbnails:
                    f.write(f"{youtube_thumbnails[video]}<br >")

        if google_confirm:
            f.write(f"<h2 id='google'>Google - <a href='#top'>Goto top</a><br></h2>")
            for post in google_posts:
                f.write(f"<a href='{post['link_url']}' target='_blank'>{post['link_title']} - {post['link_display_url']}</a><br >")
                f.write(f"{post['link_snippet']}<br ><br >")

        if book_search_confirmation:
            f.write(f"<h2 id='books'>Books - <a href='#top'>Goto top</a><br></h2>")
            f.write(f"For more accurate results, follow this link: "
                    f"<a href='https://www.google.com/search?q={search_term} book filetype:pdf' target='_blank'><b>Results</b></a><br ><br >")
            for book in google_books:
                f.write(f"<a href='{book['link_url']}' target='_blank'>{book['link_title']} - {book['link_display_url']}</a><br >")
                f.write(f"{book['link_snippet']}<br ><br >")


write_file()

if wiki_articles:
    confirm_wiki_download = check_confirmation(input("Do you want to convert Wikipedia articles to pdf? (y/n) "))
    if confirm_wiki_download:
        download_wikipedia()

if google_books:
    download_books_confirmation = check_confirmation(input("Do you want to download the books? (y/n) "))
    if download_books_confirmation:
        download_books()

if youtube_videos:
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
                              "0- 1080p\n"
                              "1- 720p\n"
                              "2- 480p\n\n"))
    if 0 > video_quality > 1:
        print("Video quality should be a number between 0 and 1 (inclusive)")
        get_video_quality()


total_size = 0
def download_youtube():
    global total_size
    get_video_quantity()
    get_video_quality()
    if video_quantity is 1:
        videos_to_download = [videos_links[0]]
    else:
        videos_to_download = videos_links[:video_quantity]

    print("Getting the total size...")
    for i_index, video in enumerate(videos_to_download):
        try:
            print(f"Getting size from video {i_index + 1} of {len(videos_to_download)}")
            yt = YouTube(video)
            streams_list = yt.streams.filter(progressive=True).order_by("resolution").desc()
            if video_quality is 0:
                my_stream = streams_list.filter(resolution="1080p").first()
                if my_stream is None:
                    print("There's no available 1080p resolution for this video")
                    my_stream = streams_list.filter(resolution="720p").first()
                    if my_stream is None:
                        my_stream = streams_list.filter(resolution="480p").first()
                        if my_stream is None:
                            my_stream = streams_list.last()
                            print(f"Lowest resolution was chosen")
                        else:
                            print(f"480p was chosen by default")
                    else:
                        print(f"720p was chosen by default")
            elif video_quality is 1:
                my_stream = streams_list.filter(resolution="720p").first()
                if my_stream is None:
                    print("There's no available 720p resolution for this video")
                    my_stream = streams_list.filter(resolution="480p").first()
                    if my_stream is None:
                        my_stream = streams_list.last()
                        print(f"Lowest resolution was chosen")
                    print(f"480p was chosen by default")
            else:
                my_stream = streams_list.filter(resolution="480p").first()
                if my_stream is None:
                    print("There's no available 480p resolution for this video")
                    my_stream = streams_list.last()
                    print(f"Lowest resolution was chosen")
            file_size = my_stream.filesize / 1000000
        except:
            pass
        else:
            total_size += file_size
    proceed = check_confirmation(input(f"\nYou're about to download about {round(total_size)} mb in videos,"
                                       f" do you want to proceed? (y/n) "))

    if not proceed:
        total_size = 0
        download_youtube()

    if not path.exists(f"{search_term}/Videos"):
        mkdir(f"{search_term}/Videos")

    for video in set(videos_to_download):
        try:
            yt = YouTube(video)
            original_title = format_string(yt.title)
            print(f"\nGetting data from \"{original_title}\"")
            streams_list = yt.streams.filter(progressive=True).order_by("resolution").desc()
            if video_quality is 0:
                my_stream = streams_list.filter(resolution="1080p").first()
                if my_stream is None:
                    print("There's no available 1080p resolution for this video")
                    my_stream = streams_list.filter(resolution="720p").first()
                    if my_stream is None:
                        my_stream = streams_list.filter(resolution="480p").first()
                        if my_stream is None:
                            my_stream = streams_list.last()
                            print(f"Lowest resolution was chosen")
                        else:
                            print(f"480p was chosen by default")
                    else:
                        print(f"720p was chosen by default")
            elif video_quality is 1:
                my_stream = streams_list.filter(resolution="720p").first()
                if my_stream is None:
                    print("There's no available 720p resolution for this video")
                    my_stream = streams_list.filter(resolution="480p").first()
                    if my_stream is None:
                        my_stream = streams_list.last()
                        print(f"Lowest resolution was chosen")
                    print(f"480p was chosen by default")
            else:
                my_stream = streams_list.filter(resolution="480p").first()
                if my_stream is None:
                    print("There's no available 480p resolution for this video")
                    my_stream = streams_list.last()
                    print(f"Lowest resolution was chosen")
            file_size = my_stream.filesize / 1000000
            print(f"\tDownloading {round(file_size)} mb...")
            identifier = randrange(0, 999999999)
            video_title = f"{original_title}_{identifier}"
            with open(f"{search_term}/Videos/{video_title}_description.txt", "w") as f:
                f.write(yt.description)
            my_stream.download(output_path=f"{search_term}/Videos/", filename=video_title)
        except:
            print(f"Wasn't able to download {video}")


if youtube_confirm and confirm_youtube_download:
    download_youtube()