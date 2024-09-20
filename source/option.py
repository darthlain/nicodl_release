from imports import *

# デバッグモード 普段使用時にtrueになってはいけない
debug = False
version = '2024-09-20'

yt_dlp = 'yt-dlp'

if debug:
    user_session_path = 'F:/download/nicodl_user_session.txt'
    option_path = 'F:/download/nicodl_option.json'
else:
    user_session_path = os.path.join(Path(sys.argv[0]).parent.resolve(),
            "nicodl_user_session.txt")

    option_path = os.path.join(Path(sys.argv[0]).parent.resolve(),
            "nicodl_option.json")

user_session = None

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

    if not a.get('comment_mail'):
        a['comment_mail'] = ''

    if not a.get('comment_pass'):
        a['comment_pass'] = ''

    if not a.get('user_session'):
        a['user_session'] = ''

    if not a.get('is_video'):
        a['is_video'] = 'true'

    if not a.get('is_comment'):
        a['is_comment'] = 'true'

    if not a.get('is_kakolog'):
        a['is_kakolog'] = 'true'

    if not a.get('is_kantan'):
        a['is_kantan'] = 'false'

    if not a.get('comment_fileformat'):
        a['comment_fileformat'] = "*title* [*id*][*comment_num*コメ].xml"

    if not a.get('end_presswait'):
        a['end_presswait'] = 'true'

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

#def debug_option(option):
#    with open('F:/download/nicodl_debug.txt', 'r', encoding = 'utf-8') as f:
#        a = f.read().splitlines()
#
#    b = copy.copy(option)
#
#    b['dl_dir'] = Path(a[0])
#    b['comment_mail'] = a[1]
#    b['comment_pass'] = a[2]
#
#    return b

def debug_option2():
    return debug_option(make_option())
