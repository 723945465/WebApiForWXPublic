# 使用提醒:
# 1. 这个模块的作用是把微信公众号推文的URL中非固定的参数去掉，这样存入数据库的就是URL中固定的部分，可以作为公号文章的标识
# 2. 传入参数param_names是一个字符串的数组

from urllib.parse import urlparse, parse_qs, urlencode


def remove_params_from_url(url, del_urlparam_names):
    # 解析URL
    parsed_url = urlparse(url)
  #  print(parsed_url)

    # 获取查询参数字典
    query_params = parse_qs(parsed_url.query)

    # 从查询参数字典中移除指定的参数
    for param_name in del_urlparam_names:
        query_params.pop(str(param_name), None)

    # 重新构建URL
    new_query = urlencode(query_params, doseq=True)
    new_url = parsed_url._replace(query=new_query).geturl()

    return new_url