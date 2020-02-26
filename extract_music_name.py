#!coding: utf-8

from get_music_list import extract_music_names
import pandas as pd
import re
from pathlib import Path
import emoji
import sys

MUSIC_URL = "https://www.uta-net.com/artist/684/"

def extract_singer_name(singer_name_candidate):
    singer_name = None
    if "【" in singer_name_candidate and "】" in singer_name_candidate:
        start = singer_name_candidate.index("【")
        end = singer_name_candidate.index("】")
        singer_name = singer_name_candidate[start+1: end]
    return singer_name

def normarize(text):
    text = text.replace(" ", "")
    text = text.replace("ー", "")
    text = text.replace("〜", "")
    # 半角か全角かわからん
    text = text.replace("―", "")
    text = text.replace("～", "")
    text = text.replace("＃", "")
    text = text.replace("#", "")

    return text

def remove_emoji(text):
    # text = text.replace("ロ", "")
    # text = text.replace("", "")
    # text = text.replace("", "")
    text =  ''.join(c for c in text if c not in emoji.UNICODE_EMOJI)

    # non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), '')
    # text = text.translate(non_bmp_map)

    text = re.sub('[\ue000-\uf8ff]+', '', text)

    return text

def calc_mutchi_num(text1, text2):
    # TODO 曲名の最初の方でスペルミスがあった場合、一致率が低くなる問題がある
    n = len(text1)
    mutchi_n = 0
    for t1, t2 in zip(text1, text2):
        mutchi_n += t1 == t2
    return mutchi_n

def search_word_high_match_rate(text, words):
    mutch_rate_line = 0.5
    mutchi_word = None
    max_mutchi_num = 0
    text = normarize(text)
    n = len(text)
    # target_wrods = [w for w in words if len(w) <= n]
    for w in words:
        w_normarize = normarize(w)
        w_n = len(w_normarize)
        
        if w_n > n:
            pad_text = text + " " * (w_n - n)
            mutchi_num = calc_mutchi_num(w_normarize, pad_text)
            mutchi_rate = mutchi_num / w_n
            if mutchi_rate > mutch_rate_line and mutchi_num > max_mutchi_num:
                mutchi_word = w
                max_mutchi_num = mutchi_num
        
        for i in range(0, n - w_n + 1):
            candidate = text[i:i+w_n]
            mutchi_num = calc_mutchi_num(w_normarize, candidate)
            mutchi_rate = mutchi_num / w_n
            if mutchi_rate > mutch_rate_line and mutchi_num > max_mutchi_num:
                mutchi_word = w
                max_mutchi_num = mutchi_num
    return mutchi_word


def extract_music_name():
    music_list = extract_music_names(MUSIC_URL)
    def extract(music_name_candidate):
        # music_name = None
        # matchi_len = 0
        # music_name_candidate = normarize(music_name_candidate)
        # # 複数一致があった場合は、一致長の長い方を返す
        # for music in music_list:
        #     # タイプミスを考慮するため、曲名との一致率で比較する
        #     if normarize(music) in music_name_candidate and matchi_len < len(music):
        #         music_name = music
        #         matchi_len = len(music)
        music_name = search_word_high_match_rate(music_name_candidate, music_list)
        return music_name
    return extract
    


class MusicRegister():
    def __init__(self):
        self.music = pd.DataFrame()
        self.current_singer = "no singer"
        self.extract = extract_music_name()

    def add_music(self, music_name_candidate):
        singer_name = extract_singer_name(music_name_candidate)
        if singer_name:
            self.current_singer = remove_emoji(singer_name)
            return
        music_name = self.extract(music_name_candidate)
        if music_name:
            add_row = pd.Series({"歌い手": self.current_singer, "楽曲": music_name})
            self.music = self.music.append(add_row, ignore_index=True)

class Extractor:
    def __init__(self):
        self.music_register = MusicRegister()

    def extract_from_texts(self, dir_):
        dir_ = Path(dir_)
        for file_path in dir_.iterdir():
            if file_path.stem == "miss_sample.txt":
                continue
            with open(file_path, "r", encoding="utf-8") as f:
                line = f.readline()
                while(line):
                    self.music_register.add_music(line)
                    line = f.readline()

if __name__ == "__main__":
    extractor = Extractor()
    extractor.extract_from_texts("data")
    extractor.music_register.music.to_csv("music_list.txt")
    extractor.music_register.music["count"] = 1
    music_count = extractor.music_register.music.groupby(["歌い手", "楽曲"]).count()
    music_count.to_csv("music_count.txt")