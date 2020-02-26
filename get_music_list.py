import requests
from bs4 import BeautifulSoup

def extract_music_names(url, music_names=[]): 
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    music_names += [n.get_text() for n in soup.select('td.td1')]

    next_page = soup.select('a:contains("次の200曲")')
    if next_page:
        next_page_url = next_page[0]["href"]
        extract_music_names(next_page_url, music_names)
    return music_names

if __name__ == "__main__":
    url = "https://www.uta-net.com/artist/684/"
    music_names = extract_music_names(url)
    print(len(music_names))