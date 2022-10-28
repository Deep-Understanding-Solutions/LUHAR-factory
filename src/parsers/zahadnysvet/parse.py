import requests
from bs4 import BeautifulSoup
import pandas as pd
import shelve

source_id = "zahadnysvet"

label = 0

sitemaps = (
    "https://zahadnysvet.sk/post-sitemap.xml",
)
db_keys = (
    f"parsed_articles_{source_id}_1",
)

session_selector_key = f"session_selector_{source_id}"

with shelve.open('counter') as db:
    try:
        key = db[session_selector_key]
    except KeyError:
        db[session_selector_key] = 0

    while db[session_selector_key] != len(db_keys):
        sitemap_data = sitemaps[db[session_selector_key]]
        req = requests.get(f"{sitemaps[db[session_selector_key]]}")
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
                        soup.find('h1', attrs={'class': 'entry-title'})
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
                content = soup.find('div', attrs={'class': 'td-post-content'}).find_all('p')
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
                        soup.find('li', attrs={'class': 'entry-category'}).find("a")
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
