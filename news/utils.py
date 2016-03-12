import logging

from bijgeschaafd import diff_match_patch
from news.parsers.baseparser import canonicalize

logger = logging.getLogger('parsers')


CHARSET_LIST = """EUC-JP GB2312 EUC-KR Big5 SHIFT_JIS windows-1252
IBM855
IBM866
ISO-8859-2
ISO-8859-5
ISO-8859-7
KOI8-R
MacCyrillic
TIS-620
windows-1250
windows-1251
windows-1253
windows-1255""".split()


def is_boring(old, new):
    oldu = canonicalize(old.decode('utf8'))
    newu = canonicalize(new.decode('utf8'))

    def extra_canonical(s):
        """Ignore changes in whitespace or the date line"""
        nondate_portion = s.split('\n', 1)[1]
        return nondate_portion.split()

    if extra_canonical(oldu) == extra_canonical(newu):
        return True

    for charset in CHARSET_LIST:
        try:
            if oldu.encode(charset) == new:
                logger.debug('Boring!')
                return True
        except UnicodeEncodeError:
            pass
    return False


def get_diff_info(old, new):
    dmp = diff_match_patch.diff_match_patch()
    dmp.Diff_Timeout = 3  # seconds; default of 1 is too little
    diff = dmp.diff_main(old, new)
    dmp.diff_cleanupSemantic(diff)
    chars_added = sum(len(text) for (sign, text) in diff if sign == 1)
    chars_removed = sum(len(text) for (sign, text) in diff if sign == -1)
    return dict(chars_added=chars_added, chars_removed=chars_removed)