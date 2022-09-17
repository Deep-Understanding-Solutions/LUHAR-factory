import requests
from bs4 import BeautifulSoup
import pandas as pd
import shelve

total_articles = (
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    1000,
    370,
)

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
db_keys = (
    "parsed_articles_rtvs_1",
    "parsed_articles_rtvs_2",
    "parsed_articles_rtvs_3",
    "parsed_articles_rtvs_4",
    "parsed_articles_rtvs_5",
    "parsed_articles_rtvs_6",
    "parsed_articles_rtvs_7",
    "parsed_articles_rtvs_8",
    "parsed_articles_rtvs_9",
    "parsed_articles_rtvs_10",
    "parsed_articles_rtvs_11",
    "parsed_articles_rtvs_12",
    "parsed_articles_rtvs_13",
    "parsed_articles_rtvs_14",
    "parsed_articles_rtvs_15",
    "parsed_articles_rtvs_16",
    "parsed_articles_rtvs_17",
    "parsed_articles_rtvs_18",
    "parsed_articles_rtvs_19",
    "parsed_articles_rtvs_20",
    "parsed_articles_rtvs_21",
    "parsed_articles_rtvs_22",
    "parsed_articles_rtvs_23",
    "parsed_articles_rtvs_24",
    "parsed_articles_rtvs_25",
    "parsed_articles_rtvs_26",
    "parsed_articles_rtvs_27",
)
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

    for article_decrement in range(total_articles[session_selector] - parsed_articles):
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
            csv_path = "src/parsers/rtvs/data.csv"
            ta3_df = pd.read_csv(csv_path)
            new_df = pd.DataFrame({"title": [title], "text": [article], "commentary": ["None"], "locality": ["None"], "category": [category],
                               "label": [label]})
            concatenated = pd.concat([ta3_df, new_df], axis=0, ignore_index=True)
            concatenated.to_csv(csv_path, index=False)
            print("Article added!")

        db[db_keys[session_selector]] += 1
        print(f"Articles parsed: {article_decrement + parsed_articles + 1} / {total_articles[session_selector]}")
    print(f"Session selector {session_selector} has been parsed.")
