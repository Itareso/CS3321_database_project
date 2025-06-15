from sanic import Blueprint
from sanic.response import text
import sanic
from sanic import Sanic, response
from sanic_session import Session
from sanic.response import text, redirect, json, ResponseStream, file_stream, file, html
import motor
import motor.motor_asyncio
from bson.objectid import ObjectId
from sanic_cors import CORS
from auth import protected, add_user_info_cookie, check_login
from mycrypt import encrypt, decrypt, DATABASE_KEY
from user import click_book
from os.path import isfile, join
import requests
from utils import get_collection, check_stared
from config import *
from pymongo import MongoClient

book = Blueprint('book', url_prefix='/api/v1/book')

@book.get("/test")
async def book_test(request):
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
    source = request.args.get("source", "arxiv")
    # id = ObjectId("6532290bd507ea15ca185e83")
    id = ObjectId("6569d43b2c9d068894c84b8f")
    document  = await get_collection(source).find_one({"_id": id})
    return json({"status": "ok"}, headers={"Access-Control-Allow-Origin": "*"})

@book.get("/info")
async def get_book_info(request):
    """
    Get detail of the book with given id
    """
    id = request.args.get("id")
    if id == None:
        return text("must query with an id", status=416, headers={"Access-Control-Allow-Origin": "*"})
    client = MongoClient('mongodb://localhost:27017')
    db = client['book']
    collection = db['books']
    document = collection.find_one({"douban_id": id})
    if document == None:
        return text("The book doesn't exists!, the book id you asked is {}".format(id), status=416, headers={"Access-Control-Allow-Origin": "*"})    
    
    await click_book(request, document["douban_id"])
    stared = await check_stared(request, id)
    ans = {
        'title': document["title"],
        'author': document["bookInfo"].get("作者", None), # 作者
        'publisher': document["bookInfo"].get("出版社", None),    # 出版社
        'publish_year': document["publish_year"],   # int(出版年[:4])
        'publish_month': document["publish_month"],  # int(出版年[-1] 或 [-2:])
        'pages': document["bookInfo"].get("页数", None),   # 页数
        'ISBN': document["bookInfo"].get("ISBN", None),    # ISBN
        'price': document["bookInfo"].get("定价", None), # 定价
        'layout': document["bookInfo"].get("装帧", None),  # 装帧
        'related_intro': document["related_intro"],
        # 'related_intro': None,
        'star_rate': document["star_rate"],  # 按照54321的顺序
        'authors': document.get("authors", []), # 作者列表，有若干字典组成, 长度在 [0, 若干]
        'shops': document.get("shops", []), # 商店列表，有若干字典组成, 长度在 [0, 若干]
        'url': document.get("url", None),
        'douban_id': document.get("douban_id", None),
        'menu': [" ".join(s.split()) for s in document["menu"]],
        'img_link': document.get("img_link", None),
        'tag': document.get("tag", None),
        'book_info': {k: v for k, v in document["bookInfo"].items() if k not in ("作者", "ISBN", "译者")},
        "stared": stared
    }
    # test_ans = {
    #     'title': "测试书籍标题",
    #     'author': "某作者", # 作者
    #     'publisher': "某某某出版社",    # 出版社
    #     'publish_year': 2025,   # int(出版年[:4])
    #     'publish_month': 5,  # int(出版年[-1] 或 [-2:])
    #     'pages': 123,   # 页数
    #     'ISBN': "1234567890123",    # ISBN
    #     'price': 38.00, # 定价
    #     'layout': "平装",  # 装帧
    #     'related_intro': "\n        \n          \n.intro p{text-indent:2em;word-break:normal;}\n\n\n    《菩提道次第广论四家合注(套装共2册)",
    #     # 'related_intro': None,
    #     'star_rate': [0.4, 0.3, 0.2, 0.05, 0.05],  # 按照54321的顺序
    #     'authors': [{
    #         "link": "https://book.douban.com/author/4629791/",
    #         "name": "鹤间和幸",
    #         "role": "作者",
    #         "douban_id": "4629791"
    #     }], # 作者列表，有若干字典组成, 长度在 [0, 若干]
    #     'shops': [{
    #         "name": "京东商城",
    #         "price": "34.00元",
    #         "link": "https://book.douban.com/link2/?lowest=3400&pre=0&vendor=jingdong&srcpage=subject&price=3400&pos=1&url=https%3A%2F%2Fitem.jd.com%2F10028200485059.html&cntvendor=1&srcsubj=10565780&type=bkbuy&subject=10565780"
    #     }], # 商店列表，有若干字典组成, 长度在 [0, 若干]
    #     'url': "https://book.douban.com/subject/10565780/",
    #     'douban_id': "10565780",
    #     'menu': ["自序", "放生", "快修", "护士", "上网"],    # [s.strip() for s in menu if "收起" not in s]
    #     'img_link': "https://img9.doubanio.com/view/subject/s/public/s27467436.jpg",
    #     'tag': "佛教",
    # }
    # return json(test_ans, headers={"Access-Control-Allow-Origin": "*"})
    return json(ans, headers={"Access-Control-Allow-Origin": "*"})

@book.get("/download")
@protected
async def download(request):
    token = request.args.get("tk")
    # if token != "u*DD@7eHbs3zE2A#":
    #     return text("no permission")
    id = request.args.get("id")
    if id == None:
        return text("must query with an id", status=416, headers={"Access-Control-Allow-Origin": "*"})    
    source = request.args.get("source", "100pdfs")
    collection = get_collection(source)
    document = await collection.find_one({"_id": ObjectId(id)})
    print(source)
    if source == "100pdfs":
        if document == None:
            return text("The book doesn't exists!, the book id you asked is {}".format(id), status=416
                        , headers={"Access-Control-Allow-Origin": "*"})
        path = document["pdf_address"]
        
        # return text("not imply")
        return await file_stream(path, filename=document["title"] + ".pdf", 
                                headers={"Access-Control-Allow-Origin": "*"})
    elif source == "arxiv":
        if document == None:
            return text("The book doesn't exists!, the book id you asked is {}".format(id), status=416
                        , headers={"Access-Control-Allow-Origin": "*"})
        arxiv_pdf = "https://arxiv.org/pdf/" + document["id"] + ".pdf"
        return redirect(arxiv_pdf, headers={"Access-Control-Allow-Origin": "*"})
    else:
        return text("not imply", status=416, headers={"Access-Control-Allow-Origin": "*"})
@book.get("/tables/img")
async def tables_img(requests):
    id = requests.args.get("id")
    if id == None:
        return text("must query with an id", status=416, headers={"Access-Control-Allow-Origin": "*"})
    source = requests.args.get("source", "100pdfs")
    collection = get_collection(source)
    document = await collection.find_one({"_id": ObjectId(id)})
    if document == None:
        return text("The book doesn't exists!, the book id you asked is {}".format(id), status=416
                    , headers={"Access-Control-Allow-Origin": "*"})
    table_num = len(document["table_rendition_address"])
    res = {}
    url = "/api/v1/book/table/img"
    for i in range(table_num):
        res[i] = url + f"?id={id}&index={i}"
    return json(res, headers={"Access-Control-Allow-Origin": "*"})

@book.get("/tables")
async def tables(requests):
    id = requests.args.get("id")
    if id == None:
        return text("must query with an id", status=416, headers={"Access-Control-Allow-Origin": "*"})
    source = requests.args.get("source", "100pdfs")
    collection = get_collection(source)
    document = await collection.find_one({"_id": ObjectId(id)})
    if document == None:
        return text("The book doesn't exists!, the book id you asked is {}".format(id), status=416
                    , headers={"Access-Control-Allow-Origin": "*"})
    table_num = len(document["csv_address"])
    res = {}
    url = "/api/v1/book/table"
    for i in range(table_num):
        res[i] = url + f"?id={id}&index={i}"
    return json(res, headers={"Access-Control-Allow-Origin": "*"})

@book.get("/table/img")
async def table_img(requests):
    id = requests.args.get("id")
    index = requests.args.get("index")
    index = int(index)
    index = 0 if index == None else index
    if id == None:
        return text("must query with an id", status=416, headers={"Access-Control-Allow-Origin": "*"})
    source = requests.args.get("source", "100pdfs")
    collection = get_collection(source)
    document = await collection.find_one({"_id": ObjectId(id)})
    if document == None:
        return text("The book doesn't exists!, the book id you asked is {}".format(id), status=416
                    , headers={"Access-Control-Allow-Origin": "*"})
    if index >= len(document["table_rendition_address"]):
        return text("The index is too large!", status=416, headers={"Access-Control-Allow-Origin": "*"})
    return await file(document["table_rendition_address"][index], mime_type="image/png", headers={"Access-Control-Allow-Origin": "*"})


@book.get("/table")
async def table(requests):
    id = requests.args.get("id")
    index = requests.args.get("index")
    index = int(index)
    index = 0 if index == None else index
    if id == None:
        return text("must query with an id", status=416, headers={"Access-Control-Allow-Origin": "*"})
    source = requests.args.get("source", "100pdfs")
    collection = get_collection(source)
    document = await collection.find_one({"_id": ObjectId(id)})
    if document == None:
        return text("The book doesn't exists!, the book id you asked is {}".format(id), status=416
                    , headers={"Access-Control-Allow-Origin": "*"})
    if index >= len(document["csv_address"]):
        return text("The index is too large!", status=416, headers={"Access-Control-Allow-Origin": "*"})
    path = "/home/share/files/100_PDF_csv/" + document["book_id"] + "/" + str(index) + ".csv"
    path = document["csv_address"][index]
    return await file_stream(path, mime_type="text/csv", headers={"Access-Control-Allow-Origin": "*"})
 

@book.get("/pics")
async def pics(requests):
    id = requests.args.get("id")
    if id == None:
        return text("must query with an id", status=416, headers={"Access-Control-Allow-Origin": "*"})
    source = requests.args.get("source", "100pdfs")
    collection = get_collection(source)
    document = await collection.find_one({"_id": ObjectId(id)})
    if document == None:
        return text("The book doesn't exists!, the book id you asked is {}".format(id), status=416
                    , headers={"Access-Control-Allow-Origin": "*"})
    table_num = len(document["pics_address"])
    res = {}
    url = "/api/v1/book/pic"
    for i in range(table_num):
        res[i] = url + f"?id={id}&index={i}"
    return json(res, headers={"Access-Control-Allow-Origin": "*"})

@book.get("/pic")
async def pic(requests):
    id = requests.args.get("id")
    index = requests.args.get("index")
    index = int(index)
    index = 0 if index == None else index
    if id == None:
        return text("must query with an id", status=416, headers={"Access-Control-Allow-Origin": "*"})
    source = requests.args.get("source", "100pdfs")
    collection = get_collection(source)
    document = await collection.find_one({"_id": ObjectId(id)})
    if document == None:
        return text("The book doesn't exists!, the book id you asked is {}".format(id), status=416
                    , headers={"Access-Control-Allow-Origin": "*"})
    if index >= len(document["pics_address"]):
        return text("The index is too large!", status=416, headers={"Access-Control-Allow-Origin": "*"})
    return await file(document["pics_address"][index], mime_type="image/png", headers={"Access-Control-Allow-Origin": "*"})
