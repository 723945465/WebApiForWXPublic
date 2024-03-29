from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error
import SQLStrPass
import WXPublicURLTools
import WXPublicContentParse

app = Flask(__name__)
db_host= '114.55.128.212'
db_databasename= 'fetchtheworld'
db_user= 'chris'
db_password= '19871127ldld'

def check_is_article_exited(title, url):
    try:
        # 连接到MySQL数据库
        connection = mysql.connector.connect(host=db_host, database=db_databasename, user=db_user, password=db_password)
        if connection.is_connected():
            cursor = connection.cursor()
            # 查询数据库中是否存在相同的title或link
            if len(url)==0:
                query = """SELECT * FROM hismsg_info WHERE info_title = %s"""
                cursor.execute(query, (title,))
            else:
                query = """SELECT * FROM hismsg_info WHERE info_title = %s OR info_internet_address = %s"""
                cursor.execute(query, (title,url))

            records = cursor.fetchall()

            return len(records) > 0  # 如果找到记录，则返回True，否则返回False
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        print(f"SQL STRING: {query}")
        return False  # 发生错误时返回False
    finally:
        # 关闭数据库连接
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_article(name_of_acc, title, content, url):
    try:
        # 连接到MySQL数据库
        connection = mysql.connector.connect(host=db_host, database=db_databasename, user=db_user, password=db_password)

        if connection.is_connected():
            cursor = connection.cursor()
            # 创建插入SQL语句
            query = """insert into hismsg_info (info_source,info_author_name,info_type,info_title,info_content,info_internet_address, info_ready_for_analysis)
                       values ('公众号', %s, '公众号推文', %s, %s, %s, 'yes')"""
            # 执行SQL语句
            cursor.execute(query, (name_of_acc, title, content, url))
            connection.commit()
            print("新公众号插入成功： \n" + ("" if name_of_acc is None else name_of_acc) + " : " + ("" if title is None else title) )
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        print(f"SQL STRING: {query}")
    finally:
        # 关闭数据库连接
        if connection.is_connected():
            cursor.close()
            connection.close()


def insert_tosend_table(name_of_acc, title, content, url):
    try:
        # 连接到MySQL数据库
        connection = mysql.connector.connect(host=db_host, database=db_databasename, user=db_user, password=db_password)

        if connection.is_connected():
            cursor = connection.cursor()

            # 创建插入SQL语句
            tosend_content = f"{name_of_acc}新发公众号推文： {title}\\n{url}"
            query = """insert into to_send_info (where_to_send,has_send,info_type,info_content,info_dwh_reletive_file_path) 
            values ('微信#01情报接受群','no','文字', %s, '')"""
            # 执行SQL语句
            cursor.execute(query, (tosend_content,))
            connection.commit()
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        print(f"SQL STRING: {query}")
    finally:
        # 关闭数据库连接
        if connection.is_connected():
            cursor.close()
            connection.close()
           # print("MySQL connection is closed")

def ensure_str(data):
    if isinstance(data, bytes):
        return data.decode('utf-8')
    return data or ''

@app.route('/webhook', methods=['POST'])
def webhook():
    data = {}
    files = {}  # 初始化files为空字典
    # print("receive new post, content type: " + request.content_type)

    if str('application/x-www-form-urlencoded') in str(request.content_type):
        # 处理表单数据
        data = request.form.to_dict()

        # 遍历所有表单字段并打印
        #for key in request.form:
        #    print(f"{key}: {request.form[key]}")

        title = ensure_str(request.form.get('title'))
        name_of_acc = ensure_str(request.form.get('mp'))
        time = ensure_str(request.form.get('time'))
        cover = ensure_str(request.form.get('cover'))
        copyright = ensure_str(request.form.get('copyright'))
        desc = ensure_str(request.form.get('desc'))
        author = ensure_str(request.form.get('author'))
        content = ensure_str(request.form.get('content'))
        link = ensure_str(request.form.get('link'))

        print("Received and extracted data")
        soup = BeautifulSoup(content, 'lxml')
        basic_text_content = soup.get_text()

        sql_pass_text_title = SQLStrPass.escape_sql_string(title)
        new_url = WXPublicURLTools.remove_params_from_url(link,["token", "chksm", "lang", "poc_token"])

        # 检查文章是否已存在
        if not check_is_article_exited(sql_pass_text_title, new_url):
            # 如果文章不存在，则继续处理并插入数据
            # 如果正文和图片OCR的整合parse成功，就用整合内容，否则就直接用正文的text
            sql_pass_text_content = SQLStrPass.escape_sql_string(basic_text_content)
            # content_with_pic_parse = WXPublicContentParse.parse_WXPublic_webpage(new_url)
            # if len(content_with_pic_parse)>0:
            #     sql_pass_text_content = SQLStrPass.escape_sql_string(content_with_pic_parse)
            #     print(content_with_pic_parse)

            insert_article(name_of_acc,sql_pass_text_title,sql_pass_text_content,new_url)
            insert_tosend_table(name_of_acc,sql_pass_text_title,sql_pass_text_content,new_url)
            return jsonify({"message": "Data received and inserted successfully"}), 200
        else:
            return jsonify({"message": "Article already exists"}), 200
        # 这里可以添加代码将数据保存到数据库或进行其他处理

        # # 打印接收到的数据（或进行其他处理）
        # print(f"Title: {title}")
        # print(f"name_of_acc: {name_of_acc}")
        # print(f"Time: {time}")
        # print(f"Cover: {cover}")
        # print(f"Copyright: {copyright}")
        # print(f"Desc: {desc}")
        # print(f"Author: {author}")
        # print(f"Content: {text_content}")
        # print(f"Link: {link}")
        # print(f"sql_pass_text_content: {sql_pass_text_content}")
        # print(f"new_url: {new_url}")
    else:
        # 推送的数据格式和预期不一致，要联系下爱小助，或者用GPT生成格式判断的代码看看
        return jsonify({"error": "Unsupported content type"}), 400


    return jsonify({"message": "Data received successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1868, debug=True)
