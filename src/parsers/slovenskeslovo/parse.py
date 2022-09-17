import requests
from bs4 import BeautifulSoup
import pandas as pd
import shelve

total_articles = 2671
label = 0
url = "https://slovenskeslovo.sk/clanok/"
db_key = "parsed_articles_slovenskeslovo"

with shelve.open('counter') as db:
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
                    soup.find('h2', attrs={'class': 'avatar-article-heading'})
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
            content = soup.find('div', attrs={'class': 'item-page'}).find_all('p')
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
            csv_path = "src/parsers/slovenskeslovo/data.csv"
            ta3_df = pd.read_csv(csv_path)
            new_df = pd.DataFrame({"title": [title], "text": [article], "commentary": ["None"], "locality": ["None"], "category": ["None"],
                               "label": [label]})
            concatenated = pd.concat([ta3_df, new_df], axis=0, ignore_index=True)
            concatenated.to_csv(csv_path, index=False)
            print("Article added!")

        db[db_key] += 1
        print(f"Articles parsed: {article_decrement + parsed_articles + 1} / {total_articles}")
