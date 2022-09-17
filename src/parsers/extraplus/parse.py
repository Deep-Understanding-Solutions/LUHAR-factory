import requests
from bs4 import BeautifulSoup
import pandas as pd
import shelve

total_articles = (14996, 5138)

label = 0

sitemaps = ("https://www.extraplus.sk/sitemap.xml?page=1", "https://www.extraplus.sk/sitemap.xml?page=2")
db_keys = ("parsed_articles_extraplus_1","parsed_articles_extraplus_2")
session_selector = 1

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

    for article_decrement in range(total_articles[session_selector] - parsed_articles):
        req = requests.get(f"{links[article_decrement + parsed_articles]}")
        soup = BeautifulSoup(req.content, 'html5lib')

        try:
            title = ""\
                .join(
                    soup.find('h1', attrs={'class': 'title'})
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
            perex = ""\
                .join(
                    soup.find('div', attrs={'class': 'perex'})
                        .get_text()
                        .strip()
                        .replace("\xa0", " ")
                        .replace("\xad", "-")
                        .replace("\r", "")
                        .replace("\n", "")
                        .splitlines()
                )
        except Exception:
            perex = ""

        try:
            content = soup.find('div', attrs={'class': 'formated-output'}).find_all('p')
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
            csv_path = "src/parsers/extraplus/data.csv"
            ta3_df = pd.read_csv(csv_path)
            new_df = pd.DataFrame({"title": [title], "text": [article], "commentary": ["None"], "locality": ["None"], "category": ["None"],
                               "label": [label]})
            concatenated = pd.concat([ta3_df, new_df], axis=0, ignore_index=True)
            concatenated.to_csv(csv_path, index=False)
            print("Article added!")

        db[db_keys[session_selector]] += 1
        print(f"Articles parsed: {article_decrement + parsed_articles + 1} / {total_articles[session_selector]}")
