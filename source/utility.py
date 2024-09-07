from imports import *

JST = timezone(timedelta(hours=+9), 'JST')

def now_unixtime():
    return int(datetime.now(JST).timestamp())

# デバッグ用
def write0(a):
    with open("F:/download/aaa.txt", "w", encoding = 'utf-8') as f:
        f.write(str(a))

# windowsの禁止文字を全角に直す
# /は微妙扱い？だがめんどいので置換してしまうことにする
# (yt-dlpが/付きのファイルを作ってるのを見た)
def win_forbidden_name_replace(s):
    s = s.replace("\\", "￥")
    s = s.replace("/", "／")
    s = s.replace(":", "：")
    s = s.replace("*", "＊")
    s = s.replace("?", "？")
    s = s.replace('"', '”')
    s = s.replace('<', '＜')
    s = s.replace('>', '＞')
    s = s.replace('|', '｜')
    return s

# リストの重複しているところを切り捨てる
# list(set(a)) だと並びがめちゃくちゃになるので作った
def list_remove_duplicates(lst):
    a = []

    for i in lst:
        if not i in a:
            a.append(i)

    return a
