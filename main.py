import requests
from sys import exit
import json

def check_quit(input_text):
    if input_text is "q":
        exit()

def check_confirmation(input_text):
    available_anwers = ("yes", "y", "yey")
    if input_text in available_anwers:
        return True
    else:
        return False


def is_strict():
    strict_confirmation = input("Do you want to perform a strict search? (y/n) ")
    check_quit(strict_confirmation)
    return check_confirmation(strict_confirmation)


search_term = input("What do you wanna search for? ")
check_quit(search_term)

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


search_wikipedia()

def write_file():
    file_name = f"information_about_{search_term}.html"
    with open(file_name, "w", encoding='utf-8-sig', ) as f:
        f.write(f"<h2>Wikipedia</h2>")
        for article in enumerate(wiki_articles):
            f.write(f"{article[1]}")
            f.write(f"<ul>")
            for link in wiki_in_links[article[0]]:
                f.write(f"<li>{link}</li>")
            f.write(f"</ul><br >")


write_file()

# print(len(wiki_articles))
# print(wiki_in_links)