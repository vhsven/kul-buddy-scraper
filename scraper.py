import os
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_hiddens(soup):
    kvps = [(kvp["name"], kvp["value"] if kvp.has_attr("value") else "")
            for kvp in soup.find_all("input", attrs={"type":"hidden"})]
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
        soup = BeautifulSoup(fp, 'html.parser')
        df["voornaam"] = [item.contents[1] for item in soup.select("div.attnboxOL > span.voornaam")]
        df["geboortedatum"] = [item.contents[1] for item in soup.select("div.attnboxOL > span.geboortedatum")]
        df["geslacht"] = [item.contents[0] for item in soup.select("div.attnboxOL > span.geslacht")]
        df["entourage"] = [item.contents[0] for item in soup.select("div.attnboxOL > span.entourage")]
        df["land"] = [item.contents[1] for item in soup.select("div.attnboxOL > span.land")]
        df["faculteit"] = [item.contents[0] for item in soup.select("div.attnboxOL > span.faculteit")]
        df["aankomstdatum"] = [item.contents[1] for item in soup.select("div.attnboxOL > span.aankomstdatum")]
        df["vertrekdatum"] = [item.contents[1] for item in soup.select("div.attnboxOL > span.vertrekdatum")]
        df["programma"] = [item.contents[0] for item in soup.select("div.attnboxOL > span.programma")]
        df["gevraagde_faculteit"] = [item.contents[1] for item in soup.select("div.attnboxOL > span.gevraagde_faculteit")]
        df["interesses"] = [item.contents[1] for item in soup.select("div.attnboxOL > span.interesses")]

    if len(df.index) > 0:
        df["Interest-ArtCulture"] = df.interesses.str.contains('Art & Culture')
        df["Interest-Cinema"] = df.interesses.str.contains('Cinema')
        df["Interest-ClassicMusic"] = df.interesses.str.contains('Classic Music')
        df["Interest-Music"] = df.interesses.str.contains('Music \(Pop, rock, ...\)')
        df["Interest-Parties"] = df.interesses.str.contains('Parties')
        df["Interest-Sports"] = df.interesses.str.contains('Sports')
        df["Interest-Travelling"] = df.interesses.str.contains('Travelling')

    return df

def main():
    today = datetime.today().strftime('%Y%m%d')
    username = os.environ['KULUSER']
    password = os.environ['KULPASS']
    html = scrape_html(username, password)
    save_file(today + ".html", html)
    df = scrape_buddies(today + ".html")
    df.to_csv(today + '.csv', index=False, encoding='utf-8')

if __name__ == "__main__":
    main()
