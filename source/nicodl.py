from imports import *
from option import *
from xenocopy import *
from comment import *
from utility import *

commentDL = None
option = None

def main(is_init = True):
    global commentDL, option

    try:
        if is_init:
            commentDL = CommentDL(make_option())

            option = commentDL.option

            if option['user_session']:
                commentDL.set_user_session(option['user_session'])

            version_show()
            print()
            option_show_safe(commentDL.option)

            if debug:
                print()
                print("*警告* デバッグモード")

            os.chdir(str(option['dl_dir']))

        download(option);

        if option['end_presswait']:
            print('press any key...')
            getch()

    except:
        traceback.print_exc()

        if option['end_presswait']:
            print('press any key...')
            getch()

def download_douga_main(urls, option):
    failed = []

    for i in urls:

        if (option['is_video']):
            try:
                os.system(str(option['yt_dlp_path']) + ' ' + i)
            except:
                traceback.print_exc()
                print('動画DL失敗 %s' % i)
                failed.append(i)

        if (option['is_comment']):

            try:
                a = commentDL.comment_dl_from_option(i)

                if a:
                    a.save_xml()
                else:
                    failed.append(i)

            except:
                traceback.print_exc()
                print('不明なエラー: %s' % i)

        if (i != urls[-1]):
            time.sleep(5)
    
    print()
    print('全部で%s件 終了' % len(urls))
    print()
    list_remove_duplicates(failed)

    print('失敗したURL: %d件' % len(failed))

    for i in failed:
        print(i)

def download(option):
    while 1:
        print()
        print('[a] (動画コメント)ダウンロード')
        #print('[z] (動画コメント)ダウンロード クリップボード監視')
        print('[s] フォルダを読んでファイル名の動画idからコメントを取得')
        print()
        print('[h] 動画DL:     %s' % ['☓', '○'][int(option['is_video'])])
        print('[t] コメントDL: %s' % ['☓', '○'][int(option['is_comment'])])
        print('[j] 過去ログDL: %s' % ['☓', '○'][int(option['is_kakolog'])])
        print('[p] 簡単コメDL: %s' % ['☓', '○'][int(option['is_kantan'])])
        print()
        print('[q] ログイン状態確認')
        print('[r] comment_mail, comment_passを使ってログイン')
        print('[0] 終了')
        key = getch()

        if (key == b'a'):
            download_douga_prompt(option)
        #elif (key == b'z'):
        #    download_douga_clipboard_prompt(option)
        elif (key == b's'):
            folderscan_prompt(option)
        elif (key == b'h'):
            option['is_video'] = option['is_video'] == False
            for i in range(5):
                print()
            print('-------------------------------------------------------')
        elif (key == b't'):
            option['is_comment'] = option['is_comment'] == False
            for i in range(5):
                print()
            print('-------------------------------------------------------')
        elif key == b'j':
            option['is_kakolog'] = option['is_kakolog'] == False
            for i in range(5):
                print()
            print('-------------------------------------------------------')
        elif key == b'p':
            option['is_kantan'] = option['is_kantan'] == False
            for i in range(5):
                print()
            print('-------------------------------------------------------')
        elif (key == b'q'):
            try:
                a = commentDL.is_user_session2()
            except:
                traceback.print_exc()
                a = False

            # '-' * 55
            print()
            print('-------------------------------------------------------')

            if a:
                print('[q]成功: ログインしています')
            else:
                print('[q]失敗: ログインしていません')

            time.sleep(0.5)

            for i in range(5):
                print()

        elif (key == b'r'):
            a = commentDL.make_user_session_login_option()

            print()
            print('-------------------------------------------------------')

            if a:
                print('[r]成功: ログインしました')
            else:
                print('[r]失敗: ログインできませんでした')

            for i in range(5):
                print()

            time.sleep(0.5)

        elif (key == b'0'):
            print('byebye')
            return
        else:
            continue

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
        a = fetch_nicozon_user_ids(url)

    b = []

    # http:をhttps:に変換
    for i in a:
        if i[0:5] == 'http:':
            b.append('https' + i[4:])
        else:
            b.append(i)

    return b

def download_douga_prompt(option):
    print()
    print('動画/投稿動画一覧/マイリスト/シリーズのURLを入力してください')
    print('入力が終了したら以下のコマンドを入力してください')
    print('クリップボードモード時は文字列をコピーしてください')
    print()
    print('DL実行: nico / メインに戻る: vid / クリップボードモード切り替え: eo')
    print('動画DL: h / コメントDL: t / 過去ログDL: j 簡単コメDL: p')
    urls = []
    clpmode = False
    clpend = None

    def f():
        for i in range(5):
            print()
        print('-------------------------------------------------------')
        print()
        print('[h] 動画DL:     %s' % ['☓', '○'][int(option['is_video'])])
        print('[t] コメントDL: %s' % ['☓', '○'][int(option['is_comment'])])
        print('[j] 過去ログDL: %s' % ['☓', '○'][int(option['is_kakolog'])])
        print('[p] 簡単コメDL: %s' % ['☓', '○'][int(option['is_kantan'])])
        print()
        print('DL実行: nico / メインに戻る: vid / クリップボードモード切り替え: eo')
        print('動画DL: h / コメントDL: t / 過去ログDL: j 簡単コメDL: p')

    while 1:
        if clpmode:
            url = 'eo'
        else:
            print('> ', end = '')
            url = input()

        try:
            if url == 'nico':
                break
            elif url == 'vid':
                for i in range(5):
                    print()
                print('-------------------------------------------------------')
                main(is_init = False)
                return
            elif url == 'h':
                option['is_video'] = option['is_video'] == False
                f()

            elif url == 't':
                option['is_comment'] = option['is_comment'] == False
                f()

            elif url == 'j':
                option['is_kakolog'] = option['is_kakolog'] == False
                f()

            elif url == 'p':
                option['is_kantan'] = option['is_kantan'] == False
                f()

            elif url == 'eo':
                if clpmode == False:
                    print('クリップボードモード開始')
                    clpmode = True

                while 1:
                    clp = pyperclip.waitForNewPaste()

                    if clp == 'nico':
                        clpend = 'nico'
                        break
                    elif clp == 'vid':
                        for i in range(5):
                            print()
                        print('-------------------------------------------------------')
                        main(is_init = False)
                        return

                    elif clp == 'h':
                        option['is_video'] = option['is_video'] == False
                        f()

                    elif clp == 't':
                        option['is_comment'] = option['is_comment'] == False
                        f()

                    elif clp == 'j':
                        option['is_kakolog'] = option['is_kakolog'] == False
                        f()

                    elif clp == 'p':
                        option['is_kantan'] = option['is_kantan'] == False
                        f()
                    
                    elif clp == 'eo':
                        print('クリップボードモード終了')
                        clpend = 'eo'
                        break
                    else:
                        urls += make_urls(clp)
                        urls = list_remove_duplicates(urls)

                        print('動画数: %d' % len(urls))

                if clpend == 'eo':
                    clpmode = False
                    clpend = None
                    continue

            else:
                urls += make_urls(url)
        except:
            traceback.print_exc()
            print('入力ミスかも')

        urls = list_remove_duplicates(urls)

        if debug:
            for i in urls:
                print(i)
        print('動画数: %d' % len(urls))

    download_douga_main(urls, option)

def download_douga_clipboard_prompt(option):
    print()
    print('動画/投稿動画一覧/マイリスト/シリーズのURLをコピーしてください')
    print('入力が終了したら nico という文字列をコピーしてください')
    urls = []

    while 1:
        url = pyperclip.waitForNewPaste()

        try:
            if url == 'nico':
                break
            else:
                urls += make_urls(url)
        except:
            traceback.print_exc()
            print('入力ミスかも')

        urls = list_remove_duplicates(urls)
        print('動画数: %d' % len(urls))

    download_douga_main(urls, option)

idheads = ['sm', 'nm', 'nl', 'so']

def folderscan_prompt(option):
    print('フォルダパスを入力して下さい')

    a = input()

    if (os.path.exists(a)):
        folderscan_main(a, option)
    else:
        print('-' * 55)
        print("フォルダが存在しません")
        for i in range(5):
            print()

def folderscan_main(p, option):
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
            a = commentDL.comment_dl_from_option(i)

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
    main()
