from imports import *
from utility import *
from option  import *

# 実データはjsonっぽい
# comment_dict['data']['threads']が配列で
# たぶん上から投稿者コメント,ユーザーコメント,かんたんコメント
# idsとkeyの取り方は今のところ適当なので観察 うまくいってるっぽいが
# idsが複数あるのが懸念事項

# 調査でcommeonではコメ番が重複していても支障はないことを確認
# 投稿者コメントを分けるとcommeon再生に支障が出るので…
# 上からowner main easyの順で書き込む noを見ればどれがどれかわかる

# かんたんコメントはいらんと思うけど いる人おるんかな

# when指定しないとニコる多いコメントは古くても表示されるとかやっぱあるらしい
# when指定すると完全に投稿順になる

# わりとコメントは消されるものらしい 当然No.も詰めない

# コメント少ない動画で数えて比較してみたけど 一致してるっぽい




#-------------------------------------------------------------------------------

# cookieにuser_sessionをつけたsessionを返す
# nicodl_user_session.txtに保存されているもので試す →
# fetch_loginでログイン処理 成功したらnicodl_user_session.txtに保存する →
# いずれも失敗した場合エラー
# sm9にアクセスしてチェックしてる 視聴履歴が汚染される
def make_user_session(option):
    session = requests.session()

    def check():
        url = 'https://www.nicovideo.jp/watch/sm9'
        vp = fetch_video_page(session, url)
        
        try:
            fetch_comment_from_video_page(session, vp, None)
        except FetchCommentException:
            return False
        return True

    a = read_user_session()

    if a:
        session.cookies.set('user_session', a)
        if check():
            return session

    if not fetch_login_from_option(session, option):
        raise MakeUserSessionException('make_user_session: ログインに失敗しました')
        return

    if check():
        write_user_session(session.cookies.get('user_session'))
        return session

    raise MakeUserSessionException('make_user_session: ログイン状態の取得に失敗しました')

def fetch_login(session, mail, pass_):
    url = 'https://account.nicovideo.jp/login/redirector?site=niconico'
    param = {'mail': mail, 'next_url': '', 'password': pass_}
    a = session.post(url, param, allow_redirects=False)

    return 'user_session' in session.cookies

def fetch_login_from_option(session, option):
    return fetch_login(session, option['comment_mail'], option['comment_pass'])

# 動画ページを読み込む コメントID キー 動画タイトルなどを読み込む
def fetch_video_page(session, url):
    
    a = session.get(url)
    b = bs(a.text, "html.parser")
    
    title = b.find('meta', attrs={'property': 'og:title'})['content']
    
    owner_str = r'\{"id":(\d+),"fork":\d+,"forkLabel":"owner'
    main_str  = r'\{"id":(\d+),"fork":\d+,"forkLabel":"main'
    easy_str  = r'\{"id":(\d+),"fork":\d+,"forkLabel":"easy'
    key_str   = r'"threadKey":"(eyJ0eXAiOiJKV1Qi.*?)"'
    
    find_ids_owner1 = re.findall(owner_str, str(b))
    find_ids_main1  = re.findall(main_str, str(b))
    find_ids_easy1  = re.findall(easy_str, str(b))
    find_key1       = re.findall(key_str, str(b))
    
    find_ids_owner2 = re.findall(html.escape(owner_str), str(b))
    find_ids_main2  = re.findall(html.escape(main_str), str(b))
    find_ids_easy2  = re.findall(html.escape(easy_str), str(b))
    find_key2       = re.findall(html.escape(key_str), str(b))
    
    id_owner = (find_ids_owner1 + find_ids_owner2)[0]
    id_main = (find_ids_main1 + find_ids_main2)[0]
    id_easy = (find_ids_easy1 + find_ids_easy2)[0]
    key = (find_key1 + find_key2)[0]

    return VideoPage(url, title, id_owner, id_main, id_easy, key)

# 動画再生ページのhtmlから取得できるデータ
class VideoPage:

    def __init__(self, url, title, id_owner, id_main, id_easy, key):
        self.url      = url
        self.title    = title
        self.id_owner = id_owner
        self.id_main  = id_main
        self.id_easy  = id_easy
        self.key      = key
        self.video_id = self.make_video_id(self.url)
        
    @staticmethod
    def make_video_id(url):
        if '?' in url:
            return url[url.rfind('/') + 1:url.find('?')]
        else:
            return url[url.rfind('/') + 1:]

class FetchCommentException(Exception):

    def __init__(self, arg=""):
        self.arg = arg

class MakeUserSessionException(Exception):

    def __init__(self, arg=""):
        self.arg = arg

# コメント取得 一回分
# ログインしていない場合when指定するとエラーになる
# 失敗するとFalseを返す
# when指定した場合一回で取れるコメントは500固定だろうか
def fetch_comment(session, id_owner, id_main, id_easy, key, when):

    params = make_params(id_owner, id_main, id_easy, key, when);
    headers = make_headers()

    a = session.post("https://public.nvcomment.nicovideo.jp/v1/threads",
            json.dumps(params), headers=headers)

    if a.status_code != 200:
         raise FetchCommentException("fetch_comment: 失敗")

    comment_dict = a.json()

    return comment_dict

def fetch_comment_from_video_page(session, video_page, when):
    a = video_page
    return fetch_comment(session, a.id_owner, a.id_main, a.id_easy, a.key, when)

forks = ['owner', 'main', 'easy']

# fetch_commentしたコメントデータをこれに集める
class Comments:

    # コメントデータのdictを取る
    def __init__(self):
        # 投稿された全コメント数
        self.comments = [defaultdict(lambda: None) for i in range(3)]

        # fetchしたjsonにかかれてある全コメント数
        self.comments_num = [None for i in range(3)]

    @property
    def owners(self):
        return self.comments[0]

    @property
    def mains(self):
        return self.comments[1]

    @property
    def easys(self):
        return self.comments[2]

    @property
    def owners_num(self):
        return self.comments_num[0]

    @property
    def mains_num(self):
        return self.comments_num[1]

    @property
    def easys_num(self):
        return self.comments_num[2]

    def update_comments_num(self, fetched_comment):

        for i in range(len(self.threads(fetched_comment))):
            self.comments_num[self.fork_i(i, fetched_comment)] \
                    = self.threads(fetched_comment)[i]['commentCount']

    def threads(self, fetched_comment):
        return fetched_comment['data']['threads']

    def threads_len(self, fetched_comment):
        return len(self.threads(fetched_comment))

    # threadsのindexを渡す owner main easyの順で0~2のどれかが返る
    def fork_i(self, i, fetched_comment):
        return forks.index(self.threads(fetched_comment)[i]['fork'])

    # fetch_commentの返り値を渡す
    def add(self, fetched_comment):

        self.update_comments_num(fetched_comment)

        for i in range(self.threads_len(fetched_comment)):
            for j in fetched_comment['data']['threads'][i]['comments']:
                c = Comment1(j)
                if not self.comments[self.fork_i(i, fetched_comment)][c.no()]:
                    self.comments[self.fork_i(i, fetched_comment)][c.no()] = c.xml()

    def show(self, d):
        for i in d.values():
            print(i)

    # 全部のforkのコメントを一つのファイルに収めることを想定
    def xml(self, video_id, last = '\n'):
        s = ""

        def f(a):
            nonlocal s
            s += a + last

        f('<?xml version="1.0" encoding="utf-8"?>')
        f('<!--BoonSutazioData=%s-->' % video_id)
        f('<packet>')

        for i in self.comments:
            for j in sorted(i.keys()):
                f(i[j])

        f('</packet>')

        return s


def threads(fetched_comment):
    return fetched_comment['data']['threads']

def next_time(i, fetched_comment):
    a = Comment1(threads(fetched_comment)[i]['comments'][0])
    return a.date()

# fork毎の全取得
def fetch_all_comment_fork(i, session, comments, video_page):
    vp = video_page

    if i == 0:
        f = lambda w: fetch_comment(session, vp.id_owner, None, None, vp.key, w)
    elif i == 1:
        f = lambda w: fetch_comment(session, None, vp.id_main, None, vp.key, w)
    elif i == 2:
        f = lambda w: fetch_comment(session, None, None, vp.id_easy, vp.key, w)
    else:
        raise Exception("fetch_all_comment_fork iエラー")

    w = now_unixtime()

    while 1:
        print('[%s - %s] %s: %s' % (vp.video_id, vp.title, forks[i], w))
        b = f(w)

        if (len(b['data']['threads'][0]['comments']) == 0):
            break
        else:
            comments.add(b)

            if w == next_time(0, b):
                # comments[0]の時刻と現在時刻が一致した場合終了なのだが
                # ココちょっと気になる
                # なんか投稿者コメントの時刻おかしい？ 自動投稿なのか？
                break
            else:
                w = next_time(0, b)

            time.sleep(5)

        #print(b['data']['threads'][0]['comments'][0])

# かんたんコメントを除く全取得
def fetch_all_comment_not_kantan(session, video_page):
    comments = Comments()
    vp = video_page

    fetch_all_comment_fork(0, session, comments, vp)
    time.sleep(5)
    fetch_all_comment_fork(1, session, comments, vp)

    return comments

# 過去ログとかんたんコメントを取らない全取得
def fetch_all_comment_not_kakolog_kantan(session, video_page):
    comments = Comments()
    vp = video_page
    a = fetch_comment(session, vp.id_owner, vp.id_main, None, vp.key, None)
    comments.add(a)
    return comments

# コメント一つに対する処理
class Comment1:

    def __init__(self, d):
        self.d = d # 生jsonデータ

    def body(self):
        return saxutils.escape(self.d['body'])

    def mail(self):
        return ' '.join(self.d['commands'])

    def vpos(self):
        return int(self.d['vposMs']) // 10

    def date(self):
        a = self.d['postedAt']
        return int(datetime.strptime(a, '%Y-%m-%dT%H:%M:%S+09:00').timestamp())

    def no(self):
        return int(self.d['no'])

    # saxutils.escapeするのは多分bodyだけでいいだろうが保証はない
    def xml(self):
        # vposMsが10で割り切れないのは想定していないので一応止める
        if self.d['vposMs'] % 10 != 0:
            raise Exception("Comment1.xml() vposMsの例外")

        a = self.d

        b = '<chat no="%s" user_id="%s" date="%s" nicoru="%s" score="%s" mail="%s" vpos="%s">%s</chat>' % (
                a['no'],           # コメント番号
                a['userId'],       # ユーザーID
                self.date(),       # コメントが投稿されたUNIX時間(JST)
                a['nicoruCount'],  # ニコる回数
                a['score'],        # たぶんフィルターに使うコメント評価
                self.mail(),       # コマンド
                self.vpos(),       # コメントが投稿された動画位置
                self.body()        # コメント本体
        )

        return b


def make_params(ids_owner, ids_main, ids_easy, key, when):
    a = { "params": {
                "targets": [],
                "language": "ja-jp"
            },
            "threadKey": key,
            #"force_184": "1",
            #"additionals": {
            #    "when": 1472730882
            #},
        }

    if ids_owner:
        a["params"]["targets"] += [{ "id": ids_owner, "fork": "owner" }]

    if ids_main:
        a["params"]["targets"] += [{ "id": ids_main, "fork": "main" }]

    if ids_easy:
        a["params"]["targets"] += [{ "id": ids_easy, "fork": "easy" }]

    if when:
        a["additionals"] = { "when": when }

    return a

def make_headers():
    a = {"x-frontend-id": "6"}
    return a

def comment_dl(url, option):

    if option['is_kakolog'] == 'true':
        try:
            session = make_user_session(option)
        except MakeUserSessionException:
            print('エラー: user_sessionの取得に失敗しました')
            print('        オプションファイルのcomment_mailとcomment_passにユーザー名とパスワードを書いて下さい')
            print('        あるいは、過去ログが必要ない場合はis_kakologにfalseと書いて下さい')
            return

        vp = fetch_video_page(session, url)
        comments = fetch_all_comment_not_kantan(session, vp)

    else:
        session = requests.session()
        vp = fetch_video_page(session, url)
        comments = fetch_all_comment_not_kakolog_kantan(session, vp)

    save_xml(comments, vp, option)

def save_xml(comments, video_page, option):
    vp = video_page

    # whileはファイル名かぶりの際の番号のため
    n = 0

    while 1:
        a = option['comment_fileformat']
        a = a.replace('*title*', vp.title)
        a = a.replace('*id*', vp.video_id)
        a = a.replace('*comment_num*', str(len(comments.owners) + len(comments.mains)))
        a = win_forbidden_name_replace(a)
        a = str(option['dl_dir'] / a)

        if n != 0:
            b = os.path.splitext(a)
            a = b[0] + ("(%d)" % n) + b[1]

        if os.path.exists(a):
            n += 1
        else:
            with open(a, "w", encoding = 'utf-8') as f:
                print(a)
                f.write(comments.xml(vp.video_id))
                break


if __name__ == '__main__':
    pass
