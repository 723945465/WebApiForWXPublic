import re
import emoji
import unicodedata
from html import unescape

def remove_invalid_chars(input_str):
    """ 移除字符串中的不可打印字符、无效 Unicode 字符、表情符号等 """
    # 解码可能的 HTML 实体字符
    input_str = unescape(input_str)
    # 使用 Unicode 标准化形式 NFKC
    normalized = unicodedata.normalize('NFKC', input_str)
    # 移除不可打印字符、Unicode 其他控制字符
    cleaned = ''.join(c for c in normalized if unicodedata.category(c) != 'Cc' and c != '\u0000')
    return cleaned


def escape_sql_string(input_str):
    """ 对SQL语句中的特殊字符进行转义处理 """
    # 移除无效字符
    cleaned_str = remove_invalid_chars(input_str)
    # 移除表情符号
    cleaned_str = emoji.demojize(cleaned_str)
    # 定义需要转义的特殊字符及其对应的转义序列
    escape_dict = {
        '\\': '\\\\',
        '"': '\\"',
        "'": "\\'",
        '\b': '\\b',
        '\n': '\\n',  # 保留换行符
        '\r': '\\r',
        '\t': '\\t'
    }
    # 使用正则表达式替换特殊字符
    escaped_str = re.sub(r'[\\"\'\\\\bnrt]', lambda match: escape_dict.get(match.group(), ''), cleaned_str)
    return escaped_str