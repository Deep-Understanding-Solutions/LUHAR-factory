import requests
from bs4 import BeautifulSoup
import pandas as pd
import shelve

total_articles_1 = 2001
total_articles_2 = 543

label = 0

sitemaps = ("https://www.protiprudu.org/sitemap-1.xml", "https://www.protiprudu.org/sitemap-2.xml")
db_keys = ("'parsed_articles_protiprudu_1'", "'parsed_articles_protiprudu_2'")
session_selector = 0

sitemap_data = sitemaps[session_selector]
req = requests.get(f"{sitemaps[session_selector]}")
soup_sitemap = BeautifulSoup(req.content, 'xml')
links = soup_sitemap.findAll('loc')
links = list(map(lambda link: link.get_text(), links))

with shelve.open('counter') as db:
    try:
        parsed_articles = db[db_keys[session_selector]]
    except KeyError:
        db[db_keys[session_selector]] = 0
        parsed_articles = 0

    for article_decrement in range(total_articles_1 - parsed_articles):
        article_id = total_articles_1 - article_decrement - parsed_articles - 1

        req = requests.get(f"{links[article_decrement + parsed_articles]}")
        soup = BeautifulSoup(req.content, 'html5lib')

        try:
            title = ""\
                .join(
                    soup.find('h1', attrs={'class': 'post-title'})
                        .get_text()
                        .strip()
                        .replace("\xa0", " ")
                        .replace("\xad", "-")
                        .replace("\r", "")
                        .replace("\n", "")
                        .splitlines()
                )
        except Exception:
            title = ""

        try:
            perex = ""
        except Exception:
            perex = ""

        try:
            content = soup.find('div', attrs={'class': 'entry'}).find_all('p')
            content = list(map(
                lambda paragraph: ""
                .join(
                    paragraph
                    .get_text()
                    .strip()
                    .replace("\xa0", " ")
                    .replace("\xad", "-")
                    .replace("\r", "")
                    .replace("\n", "")
                    .splitlines()
                ),
                content))
            article = perex.join(content)
        except Exception:
            article = ""

        if title != "" and article != "":
            csv_path = "src/parsers/protiprudu/data.csv"
            ta3_df = pd.read_csv(csv_path)
            new_df = pd.DataFrame({"title": [title], "text": [article], "commentary": ["None"], "locality": ["None"], "category": ["None"],
                               "label": [label]})
            concatenated = pd.concat([ta3_df, new_df], axis=0, ignore_index=True)
            concatenated.to_csv(csv_path, index=False)
            print("Article added!")

        db[db_keys[session_selector]] += 1
        print(f"Articles parsed: {article_decrement + parsed_articles + 1} / {total_articles_1}")
