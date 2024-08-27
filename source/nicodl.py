from imports import *
from comment import *
from option import *
from xenocopy import *

# 仕様
# nicodl 動画のURL or マイリス or 投稿動画

def main():
    option = make_option()

    try:
        print()
        print('yt_dlp_path = %s' % option['yt_dlp_path'])
        print('dl_dir      = %s' % option['dl_dir'])
        print('end_presswait = %s' % option['end_presswait'])
        print('is_video = %s' % option['is_video'])
        print('is_comment = %s' % option['is_comment'])
        print('comment_fileformat = %s' % option['comment_fileformat'])
        print()

        os.chdir(str(option['dl_dir']))
        download(option);

        if option['end_presswait'] == 'true':
            print('press any key...')
            getch()

    except:
        traceback.print_exc()

        if option['end_presswait'] == 'true':
            print('press any key...')
            getch()

# 前までの
#def download_prompt(option):
#    if len(sys.argv) >= 2:
#        url = sys.argv[1]
#    else:
#        print('URL?: ', end = '')
#        url = input()
#
#    if ('nicovideo.jp/watch' in url):
#        urls = [url]
#    elif 'series' in url:
#        urls = fetch_niconico_series_ids(url)
#    elif re.findall(r'user/\d+/mylist', url):
#        urls = fetch_nicozon_mylist_ids(url)
#    else:
#        urls = fetch_nicozon_user_ids(url)
#
#    print('全部で%s件' % len(urls))
#    print()
#
#    download_main(urls, option)

def download_douga_main(urls, option):
    for i in urls:

        if (option['is_video'] == 'true'):
            try:
                os.system(str(option['yt_dlp_path']) + ' ' + i)
            except:
                print('動画DL失敗 %s' % i)

        if (option['is_comment'] == 'true'):
            try:
                fetch_comment(i).save_xml(option)
            except:
                print('コメントDL失敗 %s' % i)

        if (i != urls[-1]):
            time.sleep(15 + random.random())
    
    print()
    print('全部で%s件 終了' % len(urls))

def download(option):
    while 1:
        print()
        print('[a] (動画コメント)ダウンロード')
        print('[z] (動画コメント)ダウンロード クリップボード監視')
        print('[s] フォルダを読んでファイル名の動画idからコメントを取得')
        print('[0] 終了')
        print()
        key = getch()

        if (key == b'a'):
            download_douga_prompt(option)
        elif (key == b'z'):
            download_douga_clipboard_prompt(option)
        elif (key == b's'):
            folderscan_prompt(option)
        elif (key == b'0'):
            print('byebye')
            return
        else:
            continue

def make_urls(url):
    if ('nicovideo.jp/watch' in url):
        return [url]
    elif 'series' in url:
        return fetch_niconico_series_ids(url)
    elif re.findall(r'user/\d+/mylist', url):
        return fetch_nicozon_mylist_ids(url)
    else:
        return fetch_nicozon_user_ids(url)

def list_remove_duplicates(lst):
    a = []

    for i in lst:
        if not i in a:
            a.append(i)

    return a

def download_douga_prompt(option):
    print()
    print('動画/投稿動画一覧/マイリスト/シリーズのURLを入力してください')
    print('入力が終了したら nico と入力して下さい')
    urls = []
    while 1:
        print('> ', end = '')
        url = input()

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
    while 1:
        a = input()

        if (os.path.exists(a)):
            break
        else:
            print("フォルダが存在しません")

    folderscan_main(a, option)

def folderscan_main(p, option):
    a = glob.glob(str(Path(p) / "*"))
    ids = []

    for i in a:
        for j in idheads:
            ids += re.findall(j + r"\d+", i)

    urls = list_remove_duplicates(urls)

    urls = ["https://www.nicovideo.jp/watch/" + i for i in ids]

    print('動画数: %d' % len(urls))

    for i in urls:
        try:
            fetch_comment(i).save_xml(option)
        except:
            print('失敗 %s' % i)

        if (i != urls[-1]):
            time.sleep(15)

    print('終了 動画数: %d' % len(urls))

if __name__ == '__main__':
    main()
