from imports import *
from utility import *

# 実データはjsonっぽい
# comment_dict['data']['threads']が配列で
# たぶん上から投稿者コメント,ユーザーコメント,かんたんコメント
# idsとkeyの取り方は今のところ適当なので観察 うまくいってるっぽいが
# idsが複数あるのが懸念事項

# 調査でcommeonではコメ番が重複していても支障はないことを確認
# 投稿者コメントを分けるとcommeon再生に支障が出るので…

# かんたんコメントはいらんと思うけど いる人おるんかな

class Session:

    def __init__(self):
        self.session = requests.session()
        self.is_login = False

    # ログインが成功したらTrueを返す
    def login(self, mail, pass_):

        url = "https://account.nicovideo.jp/login/redirector?site=niconico"
        param = {'mail': mail, 'password': pass_}

        a = self.session.post(url, param)

        if ('メールアドレスまたはパスワードが間違っています。' in a.text):
            return False
        else:
            self.is_login = True
            return True

    def get(self, *args, **kwargs):
        return self.session.get(*args)

    def post(self, *args, **kwargs):
        return self.session.post(*args)

class Comment2:

    def __init__(self, session):
        self.session = session
        self.is_fetch_video_page = False
        self.url = None
        self.title = None
        self.id_owner = None
        self.id_main  = None
        self.id_easy  = None
        self.key      = None
        self.owner_comments = dict()
        self.main_comments  = dict()

    # 動画ページを読み込む コメントID キー 動画タイトルなどを読み込む
    def fetch_video_page(self, url):
        self.is_fetch_video_page = True

        a = self.session.get(url)
        b = bs(a.text, "html.parser")

        self.url = url
        self.title = b.find('meta', attrs={'property': 'og:title'})['content']

        find_ids_owner1 = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"owner', str(b))
        find_ids_main1  = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"main', str(b))
        find_ids_easy1  = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"easy', str(b))
        find_key1 = re.findall(r'"threadKey":"(eyJ0eXAiOiJKV1Qi.*?)"', str(b))

        find_ids_owner2 = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;owner', str(b))
        find_ids_main2  = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;main', str(b))
        find_ids_easy2  = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;easy', str(b))
        find_key2 = re.findall(r'&quot;threadKey&quot;:&quot;(eyJ0eXAiOiJKV1Qi.*?)&quot;', str(b))

        self.id_owner = (find_ids_owner1 + find_ids_owner2)[0]
        self.id_main = (find_ids_main1 + find_ids_main2)[0]
        self.id_easy = (find_ids_easy1 + find_ids_easy2)[0]
        self.key = (find_key1 + find_key2)[0]

    def fetch_comment(self, when = None):
        headers = {"x-frontend-id": "6"}
        params = make_params(self.id_owner, self.id_main, self.id_easy, self.key);

        comment_dict = self.session.post("https://public.nvcomment.nicovideo.jp/v1/threads",
                json.dumps(params), headers=headers).json()

        return Comment(self.url, self.title, comment_dict)

    # ログを取らないコメント取得
    def fetch_comment_notall(self, url):
        a = requests.get(url)
        b = bs(a.text, "html.parser")

        title = b.find('meta', attrs={'property': 'og:title'})['content']

        find_ids_owner1 = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"owner', str(b))
        find_ids_main1  = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"main', str(b))
        find_ids_easy1  = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"easy', str(b))
        find_key1 = re.findall(r'"threadKey":"(eyJ0eXAiOiJKV1Qi.*?)"', str(b))

        find_ids_owner2 = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;owner', str(b))
        find_ids_main2  = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;main', str(b))
        find_ids_easy2  = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;easy', str(b))
        find_key2 = re.findall(r'&quot;threadKey&quot;:&quot;(eyJ0eXAiOiJKV1Qi.*?)&quot;', str(b))

        ids_owner = (find_ids_owner1 + find_ids_owner2)[0]
        ids_main = (find_ids_main1 + find_ids_main2)[0]
        ids_easy = (find_ids_easy1 + find_ids_easy2)[0]
        key = (find_key1 + find_key2)[0]

        headers = {"x-frontend-id": "6"}
        params = make_params(ids_owner, ids_main, ids_easy, key);

        comment_dict = requests.post("https://public.nvcomment.nicovideo.jp/v1/threads",
                json.dumps(params), headers=headers).json()

        return Comment(url, title, comment_dict)

    def fetch_comment_all(self, url):
        #if not self.is_login:
        #    raise Exception("fetch_comment_log ログインしていません")

        a = self.session.get(url)
        b = bs(a.text, "html.parser")

        title = b.find('meta', attrs={'property': 'og:title'})['content']

        find_ids_owner1 = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"owner', str(b))
        find_ids_main1  = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"main', str(b))
        find_ids_easy1  = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"easy', str(b))
        find_key1 = re.findall(r'"threadKey":"(eyJ0eXAiOiJKV1Qi.*?)"', str(b))

        find_ids_owner2 = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;owner', str(b))
        find_ids_main2  = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;main', str(b))
        find_ids_easy2  = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;easy', str(b))
        find_key2 = re.findall(r'&quot;threadKey&quot;:&quot;(eyJ0eXAiOiJKV1Qi.*?)&quot;', str(b))

        ids_owner = (find_ids_owner1 + find_ids_owner2)[0]
        ids_main = (find_ids_main1 + find_ids_main2)[0]
        ids_easy = (find_ids_easy1 + find_ids_easy2)[0]
        key = (find_key1 + find_key2)[0]

        headers = {"x-frontend-id": "6"}
        params = make_params(ids_owner, ids_main, ids_easy, key, when = int(datetime.now(JST).timestamp()));

        comment_dict = self.session.post("https://public.nvcomment.nicovideo.jp/v1/threads",
                json.dumps(params), headers=headers).json()

        return Comment(self.session, url, title)

class Comment3:
    last = "\n"

    def __init__(self, session, url, title):
        self.session = session
        self.url = url
        self.title = title
        self.owners = dict()
        self.mains = dict()

    # 動画ページ読み込み
    def fetch_videopage(self, url):
        a = self.session.get(url)
        b = bs(a.text, "html.parser")

    def fetch(self, when):

        title = b.find('meta', attrs={'property': 'og:title'})['content']

        find_ids_owner1 = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"owner', str(b))
        find_ids_main1  = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"main', str(b))
        find_ids_easy1  = re.findall(r'\{"id":(\d+),"fork":\d+,"forkLabel":"easy', str(b))
        find_key1 = re.findall(r'"threadKey":"(eyJ0eXAiOiJKV1Qi.*?)"', str(b))

        find_ids_owner2 = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;owner', str(b))
        find_ids_main2  = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;main', str(b))
        find_ids_easy2  = re.findall(r'\{&quot;id&quot;:(\d+),&quot;fork&quot;:\d+,&quot;forkLabel&quot;:&quot;easy', str(b))
        find_key2 = re.findall(r'&quot;threadKey&quot;:&quot;(eyJ0eXAiOiJKV1Qi.*?)&quot;', str(b))

        ids_owner = (find_ids_owner1 + find_ids_owner2)[0]
        ids_main = (find_ids_main1 + find_ids_main2)[0]
        ids_easy = (find_ids_easy1 + find_ids_easy2)[0]
        key = (find_key1 + find_key2)[0]

        headers = {"x-frontend-id": "6"}
        params = make_params(ids_owner, ids_main, ids_easy, key, when = int(datetime.now(JST).timestamp()));

        comment_dict = self.session.post("https://public.nvcomment.nicovideo.jp/v1/threads",
                json.dumps(params), headers=headers).json()

class Comment:
    # xmlファイル改行するかどうか 改行しなければその分データを節約できるが テキストの見栄えが非常に悪くなる
    # デバッグも辛くなるので できれば改行したい
    last = "\n"
    
    def __init__(self, url, title, comdct):
        self.url = url
        self.title = title
        self.comdct = comdct # 取得したdict(json)データ

    # iの長さ
    def comment_type_num(self):
        return len(self.comdct['data']['threads'])

    # jの長さ
    def comment_num(self, i):
        return len(self.comdct['data']['threads'][i]['comments'])

    def video_id(self):
        if '?' in self.url:
            return self.url[self.url.rfind('/') + 1:self.url.find('?')]
        else:
            return self.url[self.url.rfind('/') + 1:]

    # 動画の内部識別番号10桁
    def video_thread(self):
        return self.comdct['data']['globalComments'][0]['id']

    # 各コメント iは0~2 投稿者 閲覧者 かんたん
    def comment1(self, i, j):
        return self.comdct['data']['threads'][i]['comments'][j]

    # UNIX時間に直した
    def date1(self, i, j):
        a = self.comment1(i, j)['postedAt']
        return int(datetime.strptime(a, '%Y-%m-%dT%H:%M:%S+09:00').timestamp())

    # shita big red 184みたいなやつ
    def mail1(self, i, j):
        return ' '.join(self.comment1(i, j)['commands'])

    def xml1(self, i, j):
        # forkはコメントの種類らしい
        a = self.comment1(i, j)

        # vposMsが10で割り切れないのは想定していないので一応止める
        if a['vposMs'] % 10 != 0:
            raise Exception("vposMsの例外")

        # xmlエスケープ考慮 おそらくbodyだけ考慮すればいいと思うがはっきり言い切れない user_idとmailがグレー
        b = '<chat thread="%s" no="%s" vpos="%s" date="%s" user_id="%s" nicoru="%s" mail="%s" score="%s">%s</chat>' % (
                self.video_thread(), a['no'], int(a['vposMs']) // 10, self.date1(i, j), a['userId'], a['nicoruCount'],
                self.mail1(i, j), a['score'], saxutils.escape(a['body']))

        return b

    def to_xml(self):
        s = ""

        def f(a):
            nonlocal s
            s += a + self.last

        f('<?xml version="1.0" encoding="utf-8"?>')
        f('<!--BoonSutazioData=%s-->' % self.video_id())
        f('<packet>')
        
        # かんたんコメント取らない
        for i in range(2):
            for j in range(self.comment_num(i)):
                f(self.xml1(i, j))
        f('</packet>')

        return s

    def save_xml(self, option):

        x = self.to_xml()
        a = str(option['dl_dir'] / self.video_id())

        #if (self.comment_num(0) + self.comment_num(1) == 0):
        #    print(a, " コメント数が0")
        #    return

        n = 0
        while 1:
            a = option['comment_fileformat']
            a = a.replace('*title*', self.title)
            a = a.replace('*id*', self.video_id())
            a = a.replace('*comment_num*',
                    str(self.comment_num(0) + self.comment_num(1)))
            a = win_forbidden_name_replace(a)
            a = str(option['dl_dir'] / a)

            if n != 0:
                b = os.path.splitext(a)
                a = b[0] + "(%d)" % n + b[1]

            if os.path.exists(a):
                n += 1
            else:
                with open(a, "w", encoding = 'utf-8') as f:
                    print(a)
                    f.write(x)
                    break

def make_params(ids_owner, ids_main, ids_easy, key, when = False):
    a = { "params": {
                "targets":[ { "id": ids_owner, "fork": "owner" },
                            { "id": ids_main, "fork": "main" },
                            { "id": ids_easy, "fork": "easy" }],
                "language": "ja-jp"
            },
            "threadKey": key,
            #"force_184": "1",
            #"additionals": {
            #    "when": 1472730882
            #},
        }

    if when:
        a["additionals"] = { "when": when }

    return a

#def make_params_noeasy(ids, key):
#    return { "params": {
#                "targets":[
#                    {
#                        "id": ids,
#                        "fork": "owner"
#                    },
#                    {
#                        "id": ids,
#                        "fork": "main"
#                    }
#                ],
#                "language": "ja-jp"
#            },
#            "threadKey": key,
#            "additionals": {},
#        }

# 工事中なのでとりあえずの過去ログ取れないやつ
def comment_dl(url, option):
    a = Session()
    b = Comment2(a)
    d = b.fetch_comment_notall(url)
    d.save_xml(option)

if __name__ == '__main__':
    pass
