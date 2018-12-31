import os
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_hiddens(soup):
    kvps = [(kvp["name"], kvp["value"] if kvp.has_attr("value") else "")
            for kvp in soup.find_all("input", attrs={"type": "hidden"})]
    return dict(kvps)


def scrape_html(username, password):
    session = requests.session()

    url0 = "https://forms.kuleuven.be/a0032/"
    resp1 = session.get(url0)
    soup1 = BeautifulSoup(resp1.text, 'html.parser')
    url1 = soup1.form["action"]
    kvps1 = get_hiddens(soup1)

    resp2 = session.post(url1, data=kvps1)
    soup2 = BeautifulSoup(resp2.text, 'html.parser')
    url2 = "https://idp.kuleuven.be" + soup2.form["action"]
    kvps2 = get_hiddens(soup2)

    resp3 = session.post(url2, data=kvps2)
    soup3 = BeautifulSoup(resp3.text, 'html.parser')
    url3 = "https://idp.kuleuven.be" + soup3.form["action"]
    kvps3 = get_hiddens(soup3)
    kvps3["username"] = username
    kvps3["password"] = password

    resp4 = session.post(url3, data=kvps3)
    soup4 = BeautifulSoup(resp4.text, 'html.parser')
    url4 = soup4.form["action"]
    kvps4 = get_hiddens(soup4)

    resp5 = session.post(url4, data=kvps4)
    return resp5.text


def save_file(filename, content):
    with open(filename, "w", encoding="utf-8") as text_file:
        text_file.write(content)


def scrape_buddies(filename):
    df = pd.DataFrame()

    with open(filename, encoding='utf-8') as fp:
        pre = "div.attnboxOL > span."
        bs = BeautifulSoup(fp, 'html.parser')
        df["voornaam"] = [x.contents[1] for x in bs.select(f"{pre}voornaam")]
        df["geboortedatum"] = [x.contents[1] for x in bs.select(f"{pre}geboortedatum")]
        df["geslacht"] = [x.contents[0] for x in bs.select(f"{pre}geslacht")]
        df["entourage"] = [x.contents[0] for x in bs.select(f"{pre}entourage")]
        df["land"] = [x.contents[1] for x in bs.select(f"{pre}land")]
        df["faculteit"] = [x.contents[0] for x in bs.select(f"{pre}faculteit")]
        df["aankomstdatum"] = [x.contents[1] for x in bs.select(f"{pre}aankomstdatum")]
        df["vertrekdatum"] = [x.contents[1] for x in bs.select(f"{pre}vertrekdatum")]
        df["programma"] = [x.contents[0] for x in bs.select(f"{pre}programma")]
        df["interesses"] = [x.contents[1] for x in bs.select(f"{pre}interesses")]

    if len(df.index) > 0:
        intr = df.interesses
        df["Interest-ArtCulture"] = intr.str.contains('Art & Culture')
        df["Interest-Cinema"] = intr.str.contains('Cinema')
        df["Interest-ClassicMusic"] = intr.str.contains('Classic Music')
        df["Interest-Music"] = intr.str.contains('Music \(Pop, rock, ...\)')
        df["Interest-Parties"] = intr.str.contains('Parties')
        df["Interest-Sports"] = intr.str.contains('Sports')
        df["Interest-Travelling"] = intr.str.contains('Travelling')

    df.drop('interesses', axis=1, inplace=True)
    return df


def main():
    today = datetime.today().strftime('%Y%m%d')
    username = os.environ['KULUSER']
    password = os.environ['KULPASS']
    html = scrape_html(username, password)
    save_file(f"data/{today}.html", html)
    df = scrape_buddies(f"data/{today}.html")
    df.to_csv(f'data/{today}.csv', index=False, encoding='utf-8')


if __name__ == "__main__":
    main()
