from imports import *

yt_dlp = 'yt-dlp'

def read_option():
    a = os.path.join(Path(sys.argv[0]).parent, "nicodl_option.json")
    if os.path.exists(a):
        with open(a) as f:
            return json.load(f)
    else:
        return dict()

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

    if not a.get('end_presswait'):
        a['end_presswait'] = 'true'

    if not a.get('is_video'):
        a['is_video'] = 'true'

    if not a.get('is_comment'):
        a['is_comment'] = 'true'

    if not a.get('comment_fileformat'):
        a['comment_fileformat'] = "*title* [*id*][*comment_num*コメ].xml"

    return a
