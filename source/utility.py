from imports import *

idheads = ['sm', 'nm', 'nl', 'so']
maru = '○'
batu = '☓'

JST = timezone(timedelta(hours=+9), 'JST')

def now_unixtime():
    return int(datetime.now(JST).timestamp())

# windowsの禁止文字を全角に直す
# (yt-dlpが/付きのファイルを作ってるのを見た)
# ↑ 2026-04-05 これはBig_Solidusとかいうのらしい
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

# リスト内のidheads + 数字を含んでない文字列を消す
def list_remove_not_idheads(lst):
    a = []

    for i in lst:
        for j in idheads:
            if (len(re.findall(j + r"\d+", i)) != 0):
                a.append(i)

    return a

def space_bar():
    for i in range(5):
        print()
    print('-' * 55)

class ClipboardMode:

    def __init__(self, nicodl):
        self.nicodl = nicodl
        self.s = pyperclip.paste()
        self.lock = False # Trueの場合のみ機能する
        self.is_on = False # クリップボードモードに入っているかどうか

        self.thread = threading.Thread(
                target = self.thread_fn,
                daemon = True)

        self.thread.start()

    def thread_fn(self):
        while 1:
            if self.is_on and self.lock:
                s = pyperclip.paste()
                if self.s != s:
                    self.s = s;
                    print()
                    self.nicodl.download_command(s)
                    self.nicodl.download_info()
                    print('> ', end = '')
                    sys.stdout.flush()

            time.sleep(0.5)

    def start(self):
        print('クリップボードモード開始')
        self.is_on = True
        self.s = pyperclip.paste()

    def stop(self):
        print('クリップボードモード終了')
        self.is_on = False

    def toggle(self):
        if self.is_on:
            self.stop()
        else:
            self.start()


# 動画情報
# 動的情報取るためだけにselenium起動するのはどうなんだろう seleniumしらんけど
# なので静的データだけ取ってる なんとユーザーネームは取れなかったのでnicozonから取ってる
class VideoInfo:
    pass

# もちろんセンシティブ動画は非ログインだとうまくいかない
def fetch_video_info(url, session):
    info = VideoInfo()
    a = session.get(url)
    aa = html.unescape(a.text)
    info.url = url
    info.videoid = url[url.rfind('/') + 1:]
    #info.title = b.find('meta', attrs={'property': 'og:title'})['content']
    info.title = re.findall(r'(?<=property="og:title" content=").*?(?=" /><meta)', aa)[0]
    x = session.get('https://www.nicozon.net/watch/' + info.videoid)
    xxx = html.unescape(x.text)
    xx = bs(xxx, "html.parser")
    info.description = xx.find_all('div', class_='watch-description')[0].p.get_text()
    info.postdate = re.findall(r'(?<=uploadDate":").*?(?=","embedUrl)', aa)[0]
    info.tags = re.findall(r'(?<=name="keywords" content=").*?(?=" /><meta)', aa)[0]
    info.viewcounter = re.findall(r'(?<=userInteractionCount":).*?(?=},{)', aa)[0]
    info.commentcount = re.findall(r'(?<=commentCount":).*?(?=,"keywords")', aa)[0]

    # ユーザーIDはch動画の場合はない
    try:
        info.ownerid = re.findall(r'(?<=nicovideo.jp\\/user\\/).*?(?="}})', aa)[0]
    except:
        info.ownerid = ''

    try:
        z = session.get("https://www.nicozon.net/myvideo/" + info.ownerid)
        zz = html.unescape(z.text)
        info.username = re.findall(r'(?<=<title>).*?(?=さんの投稿動画)', zz)[0]
    except:
        info.username = ''
    return info

# nicozon版
#def fetch_video_info(url, session):
#    info = VideoInfo()
#    info.url = url
#    info.videoid = url[url.rfind('/') + 1:]
#
#    x = session.get('https://www.nicozon.net/watch/' + info.videoid)
#    xx = bs(x.text, "html.parser")
#    info.title = xx.find('meta', property='og:title').get('content')
#    info.description = xx.find_all('div', class_='watch-description')[0].p.get_text()
#    info.postdate = xx.find('div', id="watch-content").find('ul', class_='inline-ul').li.get_text()[:-3]
#
#    metaall = xx.find_all('meta')
#    for i in metaall:
#        if i.get('name') == 'keywords':
#            info.tags = i.get('content')
#
#    info.viewcounter = xx.find('div', id="watch-content").find('ul', class_='inline-ul').find_all('li')[1].get_text()[4:]
#    info.ownerid = re.findall(r'(?<=www.nicozon.net/myvideo/).*?(?=">投稿動画)', x.text)[0];
#    z = session.get("https://www.nicozon.net/myvideo/" + info.ownerid)
#    info.username = re.findall(r'(?<=<title>).*?(?=さんの投稿動画)', z.text)[0]
#    return info

def info_format_file(videoinfo):
    info = videoinfo
    s = ''
    s += f'[url]\n{info.url}\n\n'
    s += f'[upload_date]\n{info.postdate}\n\n'
    s += f'[title]\n{info.title}\n\n'
    s += f'[description]\n{info.description}\n\n'
    s += f'[tags]\n{info.tags}\n\n'
    s += f'[view_count]\n{info.viewcounter}\n\n'
    s += f'[comment_count]\n{info.commentcount}\n\n'
    s += f'[owner_id]\n{info.ownerid}\n\n'
    s += f'[owner_nickname]\n{info.username}'
    return s

def save_video_info(videoinfo, option):
    n = 0
    while 1:
        if n == 0:
            filename = f"{videoinfo.title} [{videoinfo.videoid}].txt"
        else:
            filename = f"{videoinfo.title} [{videoinfo.videoid}]({n}).txt"
        filename = win_forbidden_name_replace(filename)
        path = option['dl_dir'] / filename
        if (os.path.exists(path)):
            n += 1
            continue
        else:
            with open(path, "x", encoding = 'utf-8') as f:
                print(path)
                f.write(info_format_file(videoinfo))
                break
