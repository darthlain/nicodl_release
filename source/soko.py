# 使わないコード ここに避難

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

    b = fetch_login_from_option(session, option)

    if not b:
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

# fork毎の全取得
def fetch_all_comment_fork(i, session, option, comments, video_page):
    vp = video_page
    miss = 0

    if i == 0:
        f = lambda w: fetch_comment(session, vp.id_owner, None, None, vp.key, w)
    elif i == 1:
        f = lambda w: fetch_comment(session, None, vp.id_main, None, vp.key, w)
    elif i == 2:
        f = lambda w: fetch_comment(session, None, None, vp.id_easy, vp.key, w)
    else:
        return False

    w = now_unixtime()

    while 1:
        print('[%s - %s] %s: %s' % (vp.video_id, vp.title, forks[i], w))

        a = f(w)

        if a == False:
            # なぜか原因不明だが稀にやたら400になる動画がある
            # sessionを新しいのにしたら大丈夫になる user_sessionは変えなくても大丈夫だった
            session = make_user_session(option)
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
                # なんか投稿者コメントの時刻おかしい？ 全部一緒？
                break
            else:
                w = next_time(0, a)

            time.sleep(5)

# かんたんコメントを除く全取得
def fetch_all_comment_not_kantan(session, option, video_page):
    vp = video_page
    comments = Comments(self.session, vp, option)

    fetch_all_comment_fork(0, session, option, comments, vp)
    time.sleep(5)
    fetch_all_comment_fork(1, session, option, comments, vp)

    return comments

# 過去ログとかんたんコメントを取らない全取得
def fetch_all_comment_not_kakolog_kantan(session, video_page):
    vp = video_page
    comments = Comments(self.session, vp, option)
    a = fetch_comment(session, vp.id_owner, vp.id_main, None, vp.key, None)
    comments.add(a)
    return comments

def comment_dl(url, option):

    if option['is_kakolog'] == 'true':
        try:
            session = make_user_session(option)
        except MakeUserSessionException:
            traceback.print_exc()
            print('エラー: user_sessionの取得に失敗しました')
            print('        オプションファイルのcomment_mailとcomment_passにユーザー名とパスワードを書いて下さい')
            print('        あるいは、過去ログが必要ない場合はis_kakologにfalseと書いて下さい')
            return

        vp = fetch_video_page(session, url)
        comments = fetch_all_comment_not_kantan(session, option, vp)

    else:
        session = requests.session()
        vp = fetch_video_page(session, url)
        comments = fetch_all_comment_not_kakolog_kantan(session, vp)

    save_xml(comments, vp, option)

    def comment_dl_kakolog(self, url):
        vp = fetch_video_page(self.session, url)
        comments = Comments(vp, self.option)

        a = self.fetch_all_comment_fork(0, comments, vp)

        if a == False:
            print('%s 失敗' % url)
            return

        time.sleep(5)

        b = self.fetch_all_comment_fork(1, comments, vp)

        if b == False:
            print('%s 失敗' % url)
            return

        return comments

    def comment_dl_not_kakolog(self, url):
        vp = fetch_video_page(self.session, url)
        comments = Comments(vp, self.option)
        a = fetch_comment(self.session, vp.id_owner, vp.id_main, None, vp.key, None)

        if a == False:
            print('%s 失敗' % url)
            return

        comments.add(a)
        return comments
