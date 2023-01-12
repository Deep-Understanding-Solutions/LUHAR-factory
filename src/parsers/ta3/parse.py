import requests
from bs4 import BeautifulSoup
import pandas as pd
import shelve
import sys, getopt

opts = getopt.getopt(sys.argv, "hi:o:", ["ifile=", "ofile="])
reset = '-reset' in opts[1]

total_articles = 245923 + 1
label = 1
url = "https://ta3.com/clanok/"
db_key = "parsed_articles_ta3"

with shelve.open('counter') as db:
    if reset is True:
        db[db_key] = 0
        print("Session restored.")
        exit(0)

    try:
        parsed_articles = db[db_key]
    except KeyError:
        db[db_key] = 0
        parsed_articles = 0

    for article_decrement in range(total_articles - parsed_articles):
        article_id = total_articles - article_decrement - parsed_articles - 1

        req = requests.get(f"{url}{article_id}")
        soup = BeautifulSoup(req.content, 'html5lib')

        try:
            title = ""\
                .join(
                    soup.find('h1', attrs={'class': 'article-title'})
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
                    soup.find('div', attrs={'class': 'article-perex'})
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
            content = soup.find('div', attrs={'class': 'article-component'}).find_all('p')
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
                    soup.find('div', attrs={'class': 'headline-meta-category'})
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
            csv_path = "src/parsers/ta3/data.csv"
            df = pd.read_csv(csv_path)
            new_df = pd.DataFrame({"title": [title], "text": [article], "commentary": ["None"], "locality": ["None"], "category": [category],
                               "label": [label]})
            concatenated = pd.concat([df, new_df], axis=0, ignore_index=True)
            concatenated.to_csv(csv_path, index=False)
            print("Article added!")

        db[db_key] += 1
        print(f"Articles parsed: {article_decrement + parsed_articles + 1} / {total_articles - 1}")
