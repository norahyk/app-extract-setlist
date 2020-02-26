import requests
from bs4 import BeautifulSoup

url = "https://mixi.jp/view_bbs.pl?comm_id=6231048&id=92994168&comment_count=439"

r = requests.get(url)
soup = BeautifulSoup(r.content, "html.parser")

comments = [(date_.get_text().strip(), comment.get_text().strip()) for date_, comment in zip(
    soup.select('div.COMMUNITY_cardBlock__bbsCommentBox a.COMMUNITY_cardBlockUserInfo__date'),
    soup.select('div.COMMUNITY_cardBlock__bbsCommentBox div.COMMUNITY_cardBlockBody__item')
)]

# TODO ページネーション機能追加

print(comments)