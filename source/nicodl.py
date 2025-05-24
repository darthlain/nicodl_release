from imports import *
from option import *
from xenocopy import *
from comment import *
from utility import *

class Nicodl:
    
    # 起動時
    def __init__(self):
        self.comdl = CommentDL(make_option())
        self.cbmode = ClipboardMode(self)
        self.option = self.comdl.option
        self.urls = []

        if self.option['user_session']:
            self.comdl.set_user_session(self.option['user_session'])

        version_show()
        option_show_safe(self.option)

        if debug:
            print()
            print("*警告* デバッグモード")

        os.chdir(str(self.option['dl_dir']))

    # メイン画面
    def main(self):
        while 1:
            print()
            print('[a] (動画コメント)ダウンロード')
            print('[s] フォルダを読んでファイル名の動画idからコメントを取得')
            print()
            print('[q] ログイン状態確認')
            print('[r] comment_mail, comment_passを使ってログイン(非推奨)')
            print('[0] 終了')
            print()
            print('> ', end = '')
            key = input()

            if (key == 'a'):
                self.download()
            elif (key == 's'):
                self.folder_scan()
            elif (key == 'q'):
                try:
                    a = self.comdl.is_user_session2()
                except:
                    traceback.print_exc()
                    a = False

                space_bar()

                if a:
                    print('[q]成功: ログインしています')
                else:
                    print('[q]失敗: ログインしていません')

                time.sleep(0.5)

                space_bar()

            elif (key == 'r'):
                a = self.comdl.make_user_session_login_option()

                space_bar()

                if a:
                    print('[r]成功: ログインしました')
                else:
                    print('[r]失敗: ログインできませんでした')

                space_bar()

                time.sleep(0.5)

            elif (key == '0'):
                print('byebye')
                return
            else:
                continue

    # "dl"コマンド
    def download_execute(self):
        failed = []

        for i in self.urls:

            if (self.option['is_video']):
                try:
                    a = os.system(str(self.option['yt_dlp_path']) + ' ' + i)

                    if a != 0:
                        print('動画DL 標準出力エラー')
                        raise Exception("")
                except:
                    traceback.print_exc()
                    print('動画DL失敗 %s' % i)
                    failed.append(i)

            if (self.option['is_comment']):

                try:
                    a = self.comdl.comment_dl_from_option(i)

                    if a:
                        a.save_xml()
                    else:
                        failed.append(i)

                except:
                    traceback.print_exc()
                    print('コメントDL失敗: %s' % i)

            if (i != self.urls[-1]):
                time.sleep(5)
        
        print()
        print('全部で%s件 終了' % len(self.urls))
        print()
        failed = list_remove_duplicates(failed)

        print('失敗したURL: %d件' % len(failed))

        for i in failed:
            print(i)

        self.urls = []

    # 文字列を読み取ってなんらかのアクションを起こす
    # Trueを返したらdownload()のループ終了
    def download_command(self, s):
        try:
            if s == 'a':
                self.download_execute()
            elif s == '0':
                space_bar()
                return True
            elif s == 'z':
                self.option['is_video'] = self.option['is_video'] == False
            elif s == 'x':
                self.option['is_comment'] = self.option['is_comment'] == False
            elif s == 'c':
                self.option['is_kakolog'] = self.option['is_kakolog'] == False
            elif s == 'v':
                self.option['is_kantan'] = self.option['is_kantan'] == False
            elif s == 'p':
                self.cbmode.toggle()
            else:
                a = len(self.urls)
                self.urls += self.make_urls(s)
                b = len(self.urls)
                self.urls = list_remove_not_idheads(self.urls)
                self.urls = list_remove_duplicates(self.urls)
                c = len(self.urls)
                print(f'{b - a}件の動画が検出されました')
                print(f'{c - a}件追加されました')
        except:
            if self.option['is_dl_prompt_err_msg']:
                traceback.print_exc()
                print()
            print('エラー URLやコマンドを読み取れませんでした')

        if debug:
            for i in self.urls:
                print(i)
        # print('動画数: %d' % len(self.urls))

    def download_info(self):
        space_bar()
        print()
        print('動画DL:     %s' % ['☓', '○'][int(self.option['is_video'])])
        print('コメントDL: %s' % ['☓', '○'][int(self.option['is_comment'])])
        print('過去ログDL: %s' % ['☓', '○'][int(self.option['is_kakolog'])])
        print('簡単コメDL: %s' % ['☓', '○'][int(self.option['is_kantan'])])
        print()
        print('Clipboard:  %s' % ['☓', '◯'][self.cbmode.is_on])
        print()
        print('DL実行: a / メインに戻る: 0 / クリップボードモード切り替え: p')
        print('動画DL: z / コメントDL: x / 過去ログDL: c / 簡単コメDL: v')
        print('動画数: %d' % len(self.urls))

    @staticmethod
    def make_urls(url):
        if ('nicovideo.jp/watch' in url):
            if '?' in url:
                a = [url[0:url.index('?')]]
            else:
                a = [url]
        elif 'nicovideo.jp/series' in url:
            a = fetch_niconico_series_official_ids(url)
        elif 'series' in url:
            a = fetch_niconico_series_ids(url)
        elif re.findall(r'user/\d+/mylist', url):
            a = fetch_nicozon_mylist_ids(url)
        elif 'nicovideo.jp/mylist' in url:
            a = fetch_nicozon_mylist_ids(url)
        else:
            #a = fetch_nicozon_user_ids(url)
            a = fetch_niconico_user_ids(url)
    
        b = []

        # http:をhttps:に変換
        for i in a:
            if i[0:5] == 'http:':
                b.append('https' + i[4:])
            else:
                b.append(i)

        return b

    def download(self):
        self.urls = []

        while 1:
            self.download_info()
            print('> ', end = '')

            self.cbmode.lock = True
            a = input()
            self.cbmode.lock = False
            if self.download_command(a) == True:
                break

    def folder_scan(self):
        print('フォルダパスを入力して下さい')
        print('> ', end = '')

        a = input()

        if (os.path.exists(a)):
            self.folderscan_execute(a)
        else:
            print("フォルダが存在しません")
            space_bar()

    def folderscan_execute(self, p):
        a = glob.glob(str(Path(p) / "*"))
        ids = []
        failed = []

        for i in a:
            for j in idheads:
                ids += re.findall(j + r"\d+", i)

        urls = ["https://www.nicovideo.jp/watch/" + i for i in ids]

        urls = list_remove_duplicates(urls)

        print('動画数: %d' % len(urls))

        for i in urls:

            try:
                a = self.comdl.comment_dl_from_option(i)

                if a:
                    a.save_xml()
                else:
                    failed.append(i)

            except:
                traceback.print_exc()
                print('不明なエラー: %s' % i)


            if (i != urls[-1]):
                time.sleep(5)

        print('終了 動画数: %d' % len(urls))

        print()
        print('失敗したURL: %d件' % len(failed))
        for i in failed:
            print(i)

if __name__ == '__main__':
    a = Nicodl();
    a.main()
