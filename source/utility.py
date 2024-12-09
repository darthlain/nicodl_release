from imports import *

idheads = ['sm', 'nm', 'nl', 'so']

JST = timezone(timedelta(hours=+9), 'JST')

def now_unixtime():
    return int(datetime.now(JST).timestamp())

# デバッグ用
# def write0(a):
#     with open("F:/etc/nicodl_debug/a.txt", "w", encoding = 'utf-8') as f:
#         f.write(str(a))

# windowsの禁止文字を全角に直す
# /は微妙扱い？だがめんどいので置換してしまうことにする
# (yt-dlpが/付きのファイルを作ってるのを見た)
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

def space_bar():
    for i in range(5):
        print()
    print('-' * 55)

def pyperclip_info():
    print()
    print('pyperclipの最新バージョンではwaitForNewPasteは削除されているらしいです')
    print('pyperclipのダウングレードのコマンドは↓')
    print('pip install --force-reinstall -v pyperclip==1.8.2')
    print()
    print('クリップボードモードを終了します')

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
                    self.nicodl.download_command(s)
                    print('> ', end = '')

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
