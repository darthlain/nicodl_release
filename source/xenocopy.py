from imports import *
from utility import *

def identity(x):
    return x

# 文字列からID(マイリスト, ユーザーID)を抽出する
# 渡すのは番号かURLを想定
# 数が一つの場合それを、複数の場合最初の(preposition)の次の数を返す
def extract_id(s, preposition):
    s = str(s)
    a = re.findall(r'\d+', s)
    if len(a) >= 2:
        n = re.search(preposition, s).end()
        if n == -1:
            raise '想定外の文字列です'
        a = re.findall(r'\d+', s[n:])
    return a[0]

# 番号を受け取ってURLに変換する
def id2url(num, before, after = ''):
    return before + str(num) + after

# requests.getでhtmlを取る
def fetch_soup(url):
    text = requests.get(url).text
    soup = bs(text, 'html.parser')
    return soup

# 複数のIDをクリップボードにコピー
def copy_ids(video_ids):
    pyperclip.copy('\n'.join(video_ids))

# サイトからデータを取ってくる
def fetch(s, s2url, soup_navigate, fn = lambda d: print(d['url']), endfn = identity):
    ret = dict()
    ret['url'] = s2url(s)
    ret['soup'] = fetch_soup(ret['url'])
    ret['ids'] = []
    i = 0
    fn(ret)

    while True:
        try:
            ret['ids'].append(soup_navigate(ret['soup'], i))
            i += 1
        except:
            return endfn(ret)

def fetch_allpage(
        s, fetch_1page, loopfn = lambda d: print(d['url']), endfn = identity,
        waitnumfn = lambda: 2):
    ret = list()
    ret.append(fetch_1page(s, 1))
    page = 1

    # 同じIDを取るかfetch_1pageでエラーが出ればループから抜ける
    while True:
        loopfn(ret[-1])
        time.sleep(waitnumfn())
        try:
            page += 1
            now = fetch_1page(s, page)
            if ret[-1]['ids'][-1] == now['ids'][-1]:
                raise
            elif now['ids']:
                ret.append(now)
            else:
                raise
        except:
            return endfn(ret)

def take_ids(fetchdata_s):
    if isinstance(fetchdata_s, list):
        ret = list()
        for i in fetchdata_s:
            ret.extend(i['ids'])
        return ret
    else:
        return fetchdata_s['ids']



# サイト個別
def nicozon_mylist_s2url(s):
    return id2url(extract_id(s, 'mylist'), 'https://www.nicozon.net/mylist/')

def nicozon_user_1page_s2url(s, page = 1):
    return id2url(extract_id(s, 'user|myvideo'), 'https://www.nicozon.net/myvideo/', '/' + str(page))

def nicolog_user_1page_s2url(s, page = 1):
    return id2url(extract_id(s, 'user'), 'https://www.nicolog.jp/user/', '?page=' + str(page))


def nicozon_soup_navigate(soup, i):
    return soup.body.find(id='container').find(id='content').find_all(class_='clearfix')[1:][i].find(class_='description').find_all('p')[1].a['href']

def nicolog_soup_navigate(soup, i):
    return soup.body.find_all(class_='container')[1].find(class_='row').find(class_='col-sm-9 col-xs-12').table.find_all('tr')[1:][i].td.div.a['href'].split('/')[1]


def fetch_nicozon_1page_ids(s, page = 1):
    return fetch(s, lambda s: nicozon_user_1page_s2url(s, page), nicozon_soup_navigate, fn = lambda d: None)

def fetch_nicolog_1page_ids(s, page = 1):
    return fetch(s, lambda s: nicolog_user_1page_s2url(s, page), nicolog_soup_navigate, fn = lambda d: None)


def fetch_nicozon_mylist_ids(s):
    return fetch(s, nicozon_mylist_s2url, nicozon_soup_navigate, endfn = take_ids)

def fetch_nicolog_user_ids(s):
    return fetch_allpage(s, fetch_nicolog_1page_ids, endfn = take_ids)

def fetch_nicozon_user_ids(s):
    return fetch_allpage(s, fetch_nicozon_1page_ids, endfn = take_ids)

def fetch_allsite_user_ids(s):
    return fetch_nicolog_user_ids(s) + fetch_nicozon_user_ids(s)


def niconico_series_s2url(s, page = 1):
    a = id2url(extract_id(s, 'user'), 'https://www.nicovideo.jp/user/')
    b = id2url(extract_id(s, 'series'), a + '/series/', '?page=' + str(page))
    return b

def fetch_niconico_series_ids(s):
    def f(s, page = 1):
        aa = niconico_series_s2url(s, page)
        a = fetch_soup(aa)
        b = a.body.find_all(id='js-initial-userpage-data')[0]
        c  = re.findall(r'(?<="id":")[a-zA-Z]+\d+', str(b))
        # &quot;変換する関数作ったほうが良さそう
        c2 = re.findall(r'(?<=&quot;id&quot;:&quot;)[a-zA-Z]+\d+', str(b))
        c3 = c + c2
        d = list_remove_duplicates(c3)
        dd = ['https://www.nicovideo.jp/watch/' + i for i in d]
        e = dict()
        e['url'] = aa
        e['ids'] = dd
        return e;

    return fetch_allpage(s, f, endfn = take_ids)
#



def fetch_prompt(fetch, printstr):
    print(printstr)
    s = input()
    copy_ids(fetch(s))

def renban_prompt():
    print('ID連番 最初の番号を入力')
    start = input()
    int(start) # エラーチェック
    print('ID連番 最後の番号を入力')
    end = input()
    copy_ids(['sm' + str(i) for i in range(int(start), int(end) + 1)])

def main_prompt():
    while 1:
        print()
        print('[d] マイリスト (nicozon 削除動画含まない)')
        print('[f] 投稿動画   (nicozon + nicolog)')
        print()
        print('[w] 投稿動画   (nicolog 削除動画含む     あるはずの動画が取れてない場合あり)')
        print('[e] 投稿動画   (nicozon 削除動画含まない 確実性がある)')
        print('[s] ID連番')
        print('[l] 画面クリア')
        print('[0] 終了')
        print()
        key = getch()
        if   (key == b'd'):
            prompt = lambda: fetch_prompt(fetch_nicozon_mylist_ids, 'マイリスト(nicozon) URLかIDを入力')
        elif (key == b'f'):
            prompt = lambda: fetch_prompt(fetch_allsite_user_ids, '投稿動画 URLかIDを入力')
        elif (key == b'w'):
            prompt = lambda: fetch_prompt(fetch_nicolog_user_ids, '投稿動画(nicolog) URLかIDを入力')
        elif (key == b'e'):
            prompt = lambda: fetch_prompt(fetch_nicozon_user_ids, '投稿動画(nicozon) URLかIDを入力')
        elif (key == b's'):
            prompt = lambda: renban_prompt()
        elif (key == b'l'):
            os.system('cls')
            continue
        elif (key == b'0'):
            print('byebye')
            return
        else:
            continue
        try:
            prompt()
            print('完了')
        except:
            print('エラー やり直し')
            continue

# main_prompt()
