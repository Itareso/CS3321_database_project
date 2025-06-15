from sanic import Blueprint, text
from mycrypt import encrypt, DATABASE_KEY, decrypt
import motor
from sanic.response import json 
from auth import add_user_info_cookie, check_login, is_vip
import requests
from utils import parse_reading_history
from datetime import datetime, timedelta
from config import MONGODB_CONNECTION_STRING
import time
user = Blueprint("user", url_prefix="/api/v1/user")


async def click_book(request, douban_id):
    is_authenticated, username = await check_login(request)
    if not is_authenticated:
        return
    db = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
    client = db['book']
    users_collection = client['users']
    user_document = await users_collection.find_one({'username': username})
    assert user_document is not None

    # 确保history_list存在，如果不存在则初始化为空字典
    if "history_list" not in user_document or not isinstance(user_document["history_list"], dict):
        user_document["history_list"] = {}
    
    current_time = datetime.now()  # 使用UTC时间的datetime对象
    
    # 检查douban_id是否已存在于history_list中
    if douban_id in user_document["history_list"]:
        # 如果存在，更新点击次数和最近访问时间
        click_count = user_document["history_list"][douban_id][0] + 1
        user_document["history_list"][douban_id] = [click_count, current_time]
    else:
        # 如果不存在，创建新条目，初始点击次数为1
        user_document["history_list"][douban_id] = [1, current_time]
    
    # 更新数据库中的用户文档
    await users_collection.update_one(
        {'username': username},
        {'$set': {'history_list': user_document["history_list"]}}
    )
    
    
    return

@user.post("/signup")
async def signup(request):
    if request.form.get('username') is None:
        return json({"status": "error", "msg" : "no username"}, headers={"Access-Control-Allow-Origin": "*"})
    if request.form.get('password') is None:
        return json({"status": "error", "msg" : "no password"}, headers={"Access-Control-Allow-Origin": "*"})

    cf_headers = {"secret": "0x4AAAAAAAOBU8nIWJ4RM7e0hRYFTaCUKBU",
                  "response": request.form.get("cf-turnstile-response"),
                  }
    response = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=cf_headers)
    
    json_data = response.json()
    if json_data.get('success'):
        username = request.form.get('username')
        password = request.form.get('password')
        response = json({"status": "ok"}, headers={"Access-Control-Allow-Origin": "*"})
        db = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
        client = db['book']
        users_collection = client['users']
        count = await users_collection.count_documents({})
        if await users_collection.find_one({'username': request.form.get('username')}) is not None:
            return json({"status": "The user has been signed up!"}, status=200, headers={"Access-Control-Allow-Origin": "*"})
        
        # 使用数据库原子操作获取唯一ID
        counters_collection = client['counters']
        
        # 使用 findOneAndUpdate 的原子操作 - 这是线程安全和进程安全的
        counter_doc = await counters_collection.find_one_and_update(
            {"_id": "user_id"},
            {"$inc": {"seq": 1}},
            upsert=True,  # 如果不存在则创建
            return_document=True  # 返回更新后的文档
        )
        
        new_user_id = counter_doc["seq"]
        
        # 创建用户
        group = "user" if request.form.get("group") is None else request.form.get("group")
        user = {
            "user_id": new_user_id,
            "username": request.form.get('username'),
            "password": encrypt(request.form.get('password'), key=DATABASE_KEY),
            "group": group, 
            "history_list": [], 
            "star_list": [], 
            "rate_list": [], 
            "nick_name": "", 
            "email": "", 
            "photo_url": "", 
            "gender": "", 
            "birthday": ""
        }
        await users_collection.insert_one(user)
        
        # 设置cookie并返回响应
        response.cookies['username'] = encrypt(username)
        response.cookies['password'] = encrypt(password)
        return response
    else:
        return json({"status": "error"}, headers={"Access-Control-Allow-Origin": "*"})
        
@user.post("/login")
async def login(request):
    if request.form.get('username') is None:
        return json({"status": "error, no username"}, headers={"Access-Control-Allow-Origin": "*"})
    if request.form.get('password') is None:
        return json({"status": "error, no password"}, headers={"Access-Control-Allow-Origin": "*"})
    username = request.form.get('username')
    password = request.form.get('password')
    cf_headers = {
        "secret": "0x4AAAAAAAOBU8nIWJ4RM7e0hRYFTaCUKBU",
        "response": request.form.get("cf-turnstile-response"),
    }
    response = requests.post("https://challenges.cloudflare.com/turnstile/v0/siteverify", data=cf_headers)
    json_data = response.json()
    if not json_data.get('success'):
        return json({"status": "error"}, headers={"Access-Control-Allow-Origin": "*"})    
    db = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
    client = db['book']
    users_collection = client['users']
    user_document = await users_collection.find_one({'username': username})
    if user_document is None:
        return json({"status": "error", "msg" : "no such user"}, headers={"Access-Control-Allow-Origin": "*"})
    if password == decrypt(user_document['password'], key=DATABASE_KEY):
        response = json({"status": "ok"}, headers={"Access-Control-Allow-Origin": "*"})
        response.cookies['username'] = encrypt(username)
        response.cookies['password'] = encrypt(password)
        return response
    else:
        return json({"status": "error, username or password is wrong"}, headers={"Access-Control-Allow-Origin": "*"})

@user.get("/logout")
async def logout(request):
    past = datetime.now() - timedelta(days=1)
    response = text("ok", headers={"Access-Control-Allow-Origin": "*"})
    response.cookies['username'] = ""
    response.cookies['password'] = ""
    if 'username' in response.cookies:
        response.cookies['username']['expires'] = past
    if 'password' in response.cookies:
        response.cookies['password']['expires'] = past
    return response

@user.get("/check_login")
async def checklogin(request):
    is_authenticated, username = await check_login(request)
    if is_authenticated:
        return json({"login_in": True, "username": username}, headers={"Access-Control-Allow-Origin": "*"})
    else:
        return json({"login_in": False}, headers={"Access-Control-Allow-Origin": "*"})
    
@user.get("/check_vip")
async def check_vip(request):
    is_authenticated, username = await check_login(request)
    if is_authenticated:
        is_vip_user = await is_vip(username)
        return json({"is_vip": is_vip_user}, headers={"Access-Control-Allow-Origin": "*"})
    else:
        return json({"is_vip": False}, headers={"Access-Control-Allow-Origin": "*"})
    

@user.get("/get_user_info")
async def get_user_info(request):
    is_authenticated, username = await check_login(request)
    if not is_authenticated:
        return json({"status": "error", "msg": "not logged in"}, headers={"Access-Control-Allow-Origin": "*"})
    db = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
    client = db['book']
    users_collection = client['users']
    user_document = await users_collection.find_one({'username': username})
    if user_document is None:
        return json({"status": "error", "msg": "no such user"}, headers={"Access-Control-Allow-Origin": "*"})

    reading_history = user_document.get("history_list", {})
    star_list = user_document.get("star_list", [])
    star_book_info_lst = []
    book_collection = client['books']
    for douban_id in star_list:
        document = await book_collection.find_one({"douban_id": douban_id})
        star_book_info_lst.append({
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
        })

    user_info = {
        "nick_name": user_document.get("nickname", ""),
        "email": user_document.get("email", ""),
        "group": user_document.get("group", ""),
        "vip": user_document.get("vip", ""),
        "reading_history": parse_reading_history(reading_history),
        "photo_url": user_document.get("photo_url", ""),
        "star_list": star_book_info_lst,
        "rate_list": user_document.get("rate_list", []),
        "gender": user_document.get("gender", "null"),
        "birthday": user_document.get("birthday", "null"),
        "user_id": user_document.get("user_id", ""),
    }
    return json({"status": "ok", "user_info": user_info}, headers={"Access-Control-Allow-Origin": "*"})

@user.route("/star", methods=["POST", "GET"])
async def star(request):
    is_authenticated, username = await check_login(request)
    if not is_authenticated:
        return json({"status": "error", "msg": "not logged in"}, headers={"Access-Control-Allow-Origin": "*"})
    
    # 获取客户端和数据库引用
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
    db = client['book']
    
    if request.args.get("id") is None:
        return json({"status": "error", "msg": "no id"}, headers={"Access-Control-Allow-Origin": "*"})
    
    douban_id = request.args.get("id")
    
    # 使用事务确保两个集合的更新是原子的
    async with await client.start_session() as session:
        async with session.start_transaction():
            # 获取用户文档
            users_collection = db['users']
            user_document = await users_collection.find_one(
                {'username': username}, 
                session=session
            )
            
            if user_document is None:
                return json({"status": "error", "msg": "no such user"}, headers={"Access-Control-Allow-Origin": "*"})
            
            user_id = user_document.get("user_id")
            
            # 确保star_list存在
            if "star_list" not in user_document or not isinstance(user_document["star_list"], list):
                user_document["star_list"] = []
            
            # 检查是添加还是删除
            is_adding = douban_id not in user_document["star_list"]
            
            books_collection = db['books']

            if is_adding:
                # 添加到用户的star_list
                await users_collection.update_one(
                    {'username': username},
                    {'$addToSet': {'star_list': douban_id}},
                    session=session
                )
                
                # 添加到书籍的stared_by
                await books_collection.update_one(
                    {'douban_id': douban_id},
                    {'$addToSet': {'stared_by': user_id}},
                    session=session
                )
            else:
                # 从用户的star_list移除
                await users_collection.update_one(
                    {'username': username},
                    {'$pull': {'star_list': douban_id}},
                    session=session
                )
                
                # 从书籍的stared_by移除
                await books_collection.update_one(
                    {'douban_id': douban_id},
                    {'$pull': {'stared_by': user_id}},
                    session=session
                )
    
    # 事务已完成，返回结果
    return json({
        "status": "ok",
        "action": "added" if is_adding else "removed"
    }, headers={"Access-Control-Allow-Origin": "*"})

@user.post("/rate")
async def rate(request):
    is_authenticated, username = await check_login(request)
    if not is_authenticated:
        return json({"status": "error", "msg": "not logged in"}, headers={"Access-Control-Allow-Origin": "*"})
    db = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
    client = db['book']
    users_collection = client['users']
    user_document = await users_collection.find_one({'username': username})
    if user_document is None:
        return json({"status": "error", "msg": "no such user"}, headers={"Access-Control-Allow-Origin": "*"})

    if request.form.get("id") is None:
        return json({"status": "error", "msg": "no id"}, headers={"Access-Control-Allow-Origin": "*"})
    
    douban_id = request.form.get("id")
    rate = request.form.get("rate")
    if douban_id is None:
        return json({"status": "error", "msg": "no douban_id"}, headers={"Access-Control-Allow-Origin": "*"})
    if rate is None:
        return json({"status": "error", "msg": "no rate"}, headers={"Access-Control-Allow-Origin": "*"})
    
    # 确保rate_list存在，如果不存在则初始化为空字典
    if "rate_list" not in user_document or not isinstance(user_document["rate_list"], dict):
        user_document["rate_list"] = {}

    # 更新rate_list
    user_document["rate_list"][douban_id] = rate

    # 更新数据库中的用户文档
    await users_collection.update_one(
        {'username': username},
        {'$set': {'rate_list': user_document["rate_list"]}}
    )

    return json({"status": "ok"}, headers={"Access-Control-Allow-Origin": "*"})