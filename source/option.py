from imports import *

# デバッグモード 普段使用時にtrueになってはいけない
debug = False
version = '2024-11-22'

yt_dlp = 'yt-dlp --no-mtime'

if debug:
    user_session_path = 'F:/download/nicodl_user_session.txt'
    option_path = 'F:/download/nicodl_option.json'
else:
    user_session_path = os.path.join(Path(sys.argv[0]).parent.resolve(),
            "nicodl_user_session.txt")

    option_path = os.path.join(Path(sys.argv[0]).parent.resolve(),
            "nicodl_option.json")

def read_option():
    if os.path.exists(option_path):
        with open(option_path, encoding = 'utf-8') as f:
            return json.load(f)
    else:
        return dict()

def read_user_session():
    if os.path.exists(user_session_path):
        with open(user_session_path, encoding = 'utf-8') as f:
            # print('nicodl_user_session.txtを読み込みました')
            return f.read()[:-1]

def write_user_session(a):
    with open(user_session_path, 'w', encoding = 'utf-8') as f:
        # print('nicodl_user_session.txtに書き込みました')
        f.write(a)

def json_str(d, key, default = ''):
    if not d.get(key):
        d[key] = default

def json_bool(d, key, default):
    if d.get(key) is None or d[key] == '':
        d[key] = default
    elif isinstance(d.get(key), bool):
        pass
    elif d.get(key) == 'true':
        d[key] = True
    elif d.get(key) == 'True':
        d[key] = True
    elif d.get(key) == 'false':
        d[key] = False
    elif d.get(key) == 'False':
        d[key] = False
    else:
        raise Exception('エラー: オプションファイルのbool値の設定が間違っています')

def make_option():
    a = read_option()

    if not a.get('dl_dir'):
        a['dl_dir'] = Path(sys.argv[0]).parent

    a['dl_dir'] = Path(a['dl_dir'])

    if not a.get('yt_dlp_path'):
        if os.path.isfile(a['dl_dir'] / yt_dlp):
            a['yt_dlp_path'] = Path(a['dl_dir'] / yt_dlp)
        else:
            a['yt_dlp_path'] = yt_dlp

    json_str(a, 'comment_mail')
    json_str(a, 'comment_pass')
    json_str(a, 'user_session')

    json_bool(a, 'is_video', True)
    json_bool(a, 'is_comment', True)
    json_bool(a, 'is_kakolog', True)
    json_bool(a, 'is_kantan', False)

    json_str(a, 'comment_fileformat', "*title* [*id*][*comment_num*コメ].xml")
    json_bool(a, 'end_presswait', True)

    return a

# python3.7以前だと並びがめちゃくちゃになると思う
def option_show(option):
    for i in option.items():
        print('%s = %s' % (i[0], i[1]))

# ログイン情報に目隠し
def option_show_safe(option):
    for i in option.items():
        if i[0] == 'comment_mail' or i[0] == 'comment_pass' or i[0] == 'user_session':
            print('%s = %s' % (i[0], '*' * min(30, len(i[1]))))
        else:
            print('%s = %s' % (i[0], i[1]))

def version_show():
    s = 'NicoDL Version %s' % version
    print(s)
