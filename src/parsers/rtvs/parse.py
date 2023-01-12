import requests
from bs4 import BeautifulSoup
import pandas as pd
import shelve
import sys, getopt

opts = getopt.getopt(sys.argv, "hi:o:", ["ifile=", "ofile="])
reset = '-reset' in opts[1]

source_id = "rtvs"
label = 1

sitemaps = (
    "https://spravy.rtvs.sk/post-sitemap.xml",
    "https://spravy.rtvs.sk/post-sitemap2.xml",
    "https://spravy.rtvs.sk/post-sitemap3.xml",
    "https://spravy.rtvs.sk/post-sitemap4.xml",
    "https://spravy.rtvs.sk/post-sitemap5.xml",
    "https://spravy.rtvs.sk/post-sitemap6.xml",
    "https://spravy.rtvs.sk/post-sitemap7.xml",
    "https://spravy.rtvs.sk/post-sitemap8.xml",
    "https://spravy.rtvs.sk/post-sitemap9.xml",
    "https://spravy.rtvs.sk/post-sitemap10.xml",
    "https://spravy.rtvs.sk/post-sitemap11.xml",
    "https://spravy.rtvs.sk/post-sitemap12.xml",
    "https://spravy.rtvs.sk/post-sitemap13.xml",
    "https://spravy.rtvs.sk/post-sitemap14.xml",
    "https://spravy.rtvs.sk/post-sitemap15.xml",
    "https://spravy.rtvs.sk/post-sitemap16.xml",
    "https://spravy.rtvs.sk/post-sitemap17.xml",
    "https://spravy.rtvs.sk/post-sitemap18.xml",
    "https://spravy.rtvs.sk/post-sitemap19.xml",
    "https://spravy.rtvs.sk/post-sitemap20.xml",
    "https://spravy.rtvs.sk/post-sitemap21.xml",
    "https://spravy.rtvs.sk/post-sitemap22.xml",
    "https://spravy.rtvs.sk/post-sitemap23.xml",
    "https://spravy.rtvs.sk/post-sitemap24.xml",
    "https://spravy.rtvs.sk/post-sitemap25.xml",
    "https://spravy.rtvs.sk/post-sitemap26.xml",
    "https://spravy.rtvs.sk/post-sitemap27.xml",
)

db_keys = []
for i in range(len(sitemaps)): db_keys.append(f"parsed_articles_{source_id}_{i + 1}")

session_selector_key = f"session_selector_{source_id}"

with shelve.open('counter') as db:
    if reset is True:
        db[session_selector_key] = 0
        for i in range(len(sitemaps)):
            db[db_keys[i]] = 0
        print("Session restored.")
        exit(0)

    try:
        key = db[session_selector_key]
    except KeyError:
        db[session_selector_key] = 0

    while db[session_selector_key] != len(db_keys):
        sitemap_data = sitemaps[db["session_selector_rtvs"]]
        req = requests.get(f"{sitemaps[db['session_selector_rtvs']]}")
        soup_sitemap = BeautifulSoup(req.content, 'xml')
        links = soup_sitemap.findAll('loc')
        links = list(map(lambda link: link.get_text(), links))

        total_articles = len(links)

        try:
            parsed_articles = db[db_keys[db[session_selector_key]]]
        except KeyError:
            db[db_keys[db[session_selector_key]]] = 0
            parsed_articles = 0

        for article_decrement in range(total_articles - parsed_articles):
            req = requests.get(f"{links[article_decrement + parsed_articles]}")
            soup = BeautifulSoup(req.content, 'html5lib')

            try:
                title = ""\
                    .join(
                        soup.find('h1', attrs={'class': 'post-article__title'})
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
                        soup.find('p', attrs={'class': 'post-article__lede'})
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
                content = soup.find('section', attrs={'class': 'post-article__content'}).find_all('p')
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

            try:
                category = ""\
                    .join(
                        soup.find('span', attrs={'class': 'post-article__category'})
                            .get_text()
                            .strip()
                            .replace("\xa0", " ")
                            .replace("\xad", "-")
                            .replace("\r", "")
                            .replace("\n", "")
                            .splitlines()
                    )
            except Exception:
                category = "None"

            if title != "" and article != "":
                csv_path = f"src/parsers/{source_id}/data.csv"
                ta3_df = pd.read_csv(csv_path)
                new_df = pd.DataFrame({"title": [title], "text": [article], "commentary": ["None"], "locality": ["None"], "category": [category],
                                   "label": [label]})
                concatenated = pd.concat([ta3_df, new_df], axis=0, ignore_index=True)
                concatenated.to_csv(csv_path, index=False)

            db[db_keys[db[session_selector_key]]] += 1
            print(f"Articles parsed: {article_decrement + parsed_articles + 1} / {total_articles},\n"
                  f"Last one: {links[article_decrement + parsed_articles]},\n"
                  f"Title={title != ''}, Article={article != ''}")
        print(f"Session selector {db[session_selector_key]} has been parsed.")
        db[session_selector_key] += 1
