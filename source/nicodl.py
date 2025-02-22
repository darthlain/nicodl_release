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
            print('[h] 動画DL:     %s' % ['☓', '○'][int(self.option['is_video'])])
            print('[t] コメントDL: %s' % ['☓', '○'][int(self.option['is_comment'])])
            print('[j] 過去ログDL: %s' % ['☓', '○'][int(self.option['is_kakolog'])])
            print('[p] 簡単コメDL: %s' % ['☓', '○'][int(self.option['is_kantan'])])
            print()
            print('[q] ログイン状態確認')
            print('[r] comment_mail, comment_passを使ってログイン')
            print('[0] 終了')

            key = getch()

            if (key == b'a'):
                self.download()
            elif (key == b's'):
                self.folder_scan()
            elif (key == b'h'):
                self.option['is_video'] = self.option['is_video'] == False
                space_bar()
            elif (key == b't'):
                self.option['is_comment'] = self.option['is_comment'] == False
                space_bar()
            elif key == b'j':
                self.option['is_kakolog'] = self.option['is_kakolog'] == False
                space_bar()
            elif key == b'p':
                self.option['is_kantan'] = self.option['is_kantan'] == False
                space_bar()
            elif (key == b'q'):
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

            elif (key == b'r'):
                a = self.comdl.make_user_session_login_option()

                space_bar()

                if a:
                    print('[r]成功: ログインしました')
                else:
                    print('[r]失敗: ログインできませんでした')

                space_bar()

                time.sleep(0.5)

            elif (key == b'0'):
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
                    os.system(str(self.option['yt_dlp_path']) + ' ' + i)
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
        list_remove_duplicates(failed)

        print('失敗したURL: %d件' % len(failed))

        for i in failed:
            print(i)

        self.urls = []

    # 文字列を読み取ってなんらかのアクションを起こす
    def download_command(self, s):
        try:
            if s == 'dl':
                self.download_execute()
            elif s == 'back':
                space_bar()
                self.main()
                return
            elif s == 'video':
                self.option['is_video'] = self.option['is_video'] == False
                self.download_info()
            elif s == 'com':
                self.option['is_comment'] = self.option['is_comment'] == False
                self.download_info()
            elif s == 'log':
                self.option['is_kakolog'] = self.option['is_kakolog'] == False
                self.download_info()
            elif s == 'easy':
                self.option['is_kantan'] = self.option['is_kantan'] == False
                self.download_info()
            elif s == 'cp':
                self.cbmode.toggle()
            else:
                a = len(self.urls)
                self.urls += self.make_urls(s)
                b = len(self.urls)
                self.urls = list_remove_duplicates(self.urls)
                c = len(self.urls)
                print(f'{b - a}件の動画が検出されました')
                print(f'{c - a}件追加されました')
        except:
            if self.option['is_dl_prompt_err_msg']:
                traceback.print_exc()
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
        print('DL実行: dl / メインに戻る: back / クリップボードモード切り替え: cp')
        print('動画DL: video / コメントDL: com / 過去ログDL: log / 簡単コメDL: easy')
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
        #print()
        #print('動画/投稿動画一覧/マイリスト/シリーズのURLを入力してください')
        #print('入力が終了したら以下のコマンドを入力してください')
        #print('クリップボードモード時は文字列をコピーしてください')
        #print()
        #print('DL実行: dl / メインに戻る: back / クリップボードモード切り替え: cp')
        #print('動画DL: video / コメントDL: com / 過去ログDL: log / 簡単コメDL: easy')
        self.urls = []

        while 1:
            self.download_info()
            print('> ', end = '')

            self.cbmode.lock = True
            a = input()
            self.cbmode.lock = False
            self.download_command(a)

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
