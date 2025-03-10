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

# なんかニコニコのサイトは"が&quot;になってしまうことがあるらしい？
# どっちのケースもあるのが不思議




#-------------------------------------------------------------------------------

forks = ['owner', 'main', 'easy']

# 動画ページを読み込む コメントID キー 動画タイトルなどを読み込む
def fetch_video_page(session, url):
    
    a = session.get(url)
    #print('[GET] %s' % url)

    if a.status_code != 200:
        print('エラー: %sを読み込めませんでした' % url)
        return False

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

# コメント取得 一回分
# ログインしていない場合when指定するとエラーになる
# 失敗するとFalseを返す
def fetch_comment(session, id_owner, id_main, id_easy, key, when):

    params = make_params(id_owner, id_main, id_easy, key, when);
    headers = make_headers()

    #print('[POST] https://public.nvcomment.nicovideo.jp/v1/threads')
    a = session.post("https://public.nvcomment.nicovideo.jp/v1/threads",
            json.dumps(params), headers=headers)

    if a.status_code != 200:
        return False

    comment_dict = a.json()

    return comment_dict

def fetch_comment_from_video_page(session, video_page, when):
    a = video_page
    return fetch_comment(session, a.id_owner, a.id_main, a.id_easy, a.key, when)

def threads(fetched_comment):
    return fetched_comment['data']['threads']

def next_time(i, fetched_comment):
    a = Comment1(threads(fetched_comment)[i]['comments'][0])
    return a.date()

def make_params(ids_owner, ids_main, ids_easy, key, when):
    a = { "params": {
                "targets": [],
                "language": "ja-jp"
            },
            "threadKey": key,
            #"force_184": "1",
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

def save_xml(comments, video_page, option):
    vp = video_page

    # whileはファイル名かぶりの際の番号のため
    n = 0

    while 1:
        a = option['comment_fileformat']
        a = a.replace('*title*', vp.title)
        a = a.replace('*id*', vp.video_id)
        a = a.replace('*comment_num*', str(len(comments.owners) + len(comments.mains) + len(comments.easys)))
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

class FetchCommentException(Exception):

    def __init__(self, arg=""):
        self.arg = arg

class MakeUserSessionException(Exception):

    def __init__(self, arg=""):
        self.arg = arg

# ------------------------------------------------------------------------------
# ここからクラス


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

# fetch_commentしたコメントデータをこれに集める
class Comments:

    # コメントデータのdictを取る
    def __init__(self, video_page, option):
        # 投稿された全コメント数
        self.comments = [defaultdict(lambda: None) for i in range(3)]
        self.video_page = video_page
        self.option = option

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

    def save_xml(self):
        save_xml(self, self.video_page, self.option)

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
                self.date(),       # コメントが投稿されたUNIX時間(JST固定)
                a['nicoruCount'],  # ニコる回数
                a['score'],        # たぶんフィルターに使うコメント評価
                self.mail(),       # コマンド
                self.vpos(),       # コメントが投稿された動画位置
                self.body()        # コメント本体
        )

        return b

# コメントDLのメインクラス的な
class CommentDL:

    def __init__(self, option):
        self.option = option
        self.session = requests.session()

    # sessionにuser_sessionがあるか確かめるだけ 実際に使えるかは確かめない
    def is_user_session(self):
        return self.get_user_session() != None

    def get_user_session(self):
        return self.session.cookies.get('user_session')

    def set_user_session(self, a):
        return self.session.cookies.set('user_session', a)

    # sessionがログイン状態で使えるか確かめる sm9にアクセスする
    def is_user_session2(self):
        url = 'https://www.nicovideo.jp/watch/sm9'
        vp = fetch_video_page(self.session, url)

        a = fetch_comment_from_video_page(self.session, vp, 1284887748)

        return a != False

    # user_sessionをそのままにあたらしいsessionに入れ替える
    # fetch_all_comment_forkの謎エラー用
    def replace_session(self):
        a = self.get_user_session()

        self.session = requests.session()

        if a != None:
            self.set_user_session(a)

    # user_sessionをログインで取得する 2段階認証の対策はまだ
    def make_user_session_login(self, mail, pass_):
        url = 'https://account.nicovideo.jp/login/redirector?site=niconico'
        param = {'mail': mail, 'next_url': '', 'password': pass_}
        session = requests.session()

        session.post(url, param, allow_redirects = False)

        if 'user_session' in session.cookies:
            self.session = session
            return True
        else:
            return False

    # optionからuser_sessionを読み取りログインする
    def make_user_session_login_option(self):
        if self.option['comment_mail'] and self.option['comment_pass']:

            return self.make_user_session_login(
                    self.option['comment_mail'], self.option['comment_pass'])

        else:
            return False

    def fetch_video_page(self, url):
        return fetch_video_page(self.session, url)

    def fetch_comment(self, *args):
        return fetch_comment(self.session, *args)

    # nicodl_user_session.txtから読み取る
    def make_user_session_txt(self):
        a = read_user_session()

        if a != None:
            self.set_user_session(a)
            return True
        return False

    # fork一つをすべてDLする 渡したcommentsに結果が返る
    def fetch_all_comment_fork(self, i, comments, video_page, url):
        vp = video_page
        miss = 0

        if i == 0:
            f = lambda w: fetch_comment(self.session, vp.id_owner, None, None, vp.key, w)
        elif i == 1:
            f = lambda w: fetch_comment(self.session, None, vp.id_main, None, vp.key, w)
        elif i == 2:
            f = lambda w: fetch_comment(self.session, None, None, vp.id_easy, vp.key, w)
        else:
            return False

        w = now_unixtime()

        while 1:
            print('[%s - %s] %s: %s' % (vp.video_id, vp.title, forks[i], w))

            a = f(w)

            if a == False:
                # なぜか原因不明だが稀にやたら400になる動画がある
                # sessionを新しいのにしたら大丈夫になる user_sessionは変えなくても大丈夫だった
                # 2024/12/09 sm43662224で必ず失敗する問題 vp作り直したら成功した
                self.replace_session()
                vp = self.fetch_video_page(url)
                miss += 1
                time.sleep(5)

                if miss >= 5:
                    print('[%s - %s] 5回以上失敗しました 終了' % (vp.video_id, vp.title))
                    return False

                continue

            miss = 0

            if (len(a['data']['threads'][0]['comments']) == 0):
                break
            else:
                comments.add(a)

                if w == next_time(0, a):
                    # comments[0]の時刻と現在時刻が一致した場合終了なのだが
                    # ココちょっと気になる
                    # なんか投稿者コメントの時刻おかしい？ 自動投稿なのか？
                    return True
                else:
                    w = next_time(0, a)

                time.sleep(5)

    # 過去ログDLにはsessionに有効なuser_session cookieが適用されている必要がある
    # 返り値はコメントが読み込まれたComments
    def comment_dl(self, url, is_owner, is_main, is_easy, is_kakolog):

        if is_kakolog and not self.is_user_session():
            print('エラー: user_sessionが設定されていません')
            return

        vp = fetch_video_page(self.session, url)

        if vp == False:
            return False

        time.sleep(5)
        comments = Comments(vp, self.option)

        if is_kakolog:

            lst = []
            if is_owner:
                lst.append(0)
            if is_main:
                lst.append(1)
            if is_easy:
                lst.append(2)

            for i in lst:
                a = self.fetch_all_comment_fork(i, comments, vp, url)

                if a == False:
                    print('%s 失敗1' % url)
                    return

                if lst[-1] != i:
                    time.sleep(5)

            return comments

        else:
            a = fetch_comment(self.session, vp.id_owner, vp.id_main, vp.id_easy, vp.key, None)

            if a == False:
                print('%s 失敗2' % url)
                return

            comments.add(a)
            return comments

    # is_commentは考慮しない
    def comment_dl_from_option(self, url):
        is_kakolog = self.option['is_kakolog']
        is_easy = self.option['is_kantan']

        return self.comment_dl(url, True, True, is_easy, is_kakolog)

if __name__ == '__main__':
    #a = CommentDL(make_option())
    #a.set_user_session(a.option['user_session'])
    #b = a.comment_dl_from_option('https://www.nicovideo.jp/watch/sm9')

    a = CommentDL(make_option())
    a.set_user_session(a.option['user_session'])
    print(a.option['user_session'])
    #vp = a.fetch_video_page('https://www.nicovideo.jp/watch/sm43662224')
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1733707138)
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1733707143)
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1723266301)
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1714538193)
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1713763834)
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1713418439)
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1713282216)
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1713240089)
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1713194671)
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1713171266)
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1713133802)
    #b = a.fetch_comment(None, vp.id_main, None, vp.key, 1713129550)
    pass
