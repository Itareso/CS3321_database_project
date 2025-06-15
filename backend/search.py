from sanic import Blueprint
from sanic.response import json, text
from bson.objectid import ObjectId
search = Blueprint("search", url_prefix="/api/v1/search")
from utils import get_collection, check_stared
from auth import check_login
from config import MONGODB_CONNECTION_STRING
import motor

def search_by_title(collection, keyword):
    """
    返回 title 包含 keyword（不区分大小写）的所有书籍列表
    """
    regex = {"$regex": keyword, "$options": "i"}
    cursor = collection.find({"title": regex})
    return cursor

# # 使用示例
# results = search_by_title(collection, "帝王")
# for book in results:
#     print(book["title"], book["douban_id"])

def search_by_author(collection, author_name):
    """
    返回 authors 数组中 name 等于或包含 author_name 的所有书籍
    """
    # 精确匹配
    # query = {"authors.name": author_name}
    
    # 模糊匹配（部分匹配／大小写不敏感）
    query = {"authors.name": {"$regex": author_name, "$options": "i"}}
    
    cursor = collection.find(query)
    return cursor

# # 使用示例
# author_results = search_by_author(collection, "苏童")
# for book in author_results:
#     print([a["name"] for a in book["authors"]], "→", book["title"])

@search.get("/")
async def searcher(request):
    query_field = request.args.get("field") if request.args.get("field") is not None else "recommend"  # title \ author
    collection = get_collection("books")
    if collection == None:
        return text("source not imply", status=416, headers={"Access-Control-Allow-Origin": "*"})
    query = request.args.get("info")
    if query == None and query_field != "recommend":
        return text("must request with a query", status=416, headers={"Access-Control-Allow-Origin": "*"})

    max_length = request.args.get("max_length") if request.args.get("max_length") is not None else 10
    is_authenticated, user_name = await check_login(request)
    if not is_authenticated:
        user_id = None
    else:
        db = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
        client = db['book']
        users_collection = client['users']
        user_document = await users_collection.find_one({'username': user_name})
        user_id = user_document['user_id'] if user_document else 1
    if query_field == "recommend":
        book_ids = request.app.ctx.recommender.recommend_by_user(user_id, top_k=max_length)
        results_to_return = []
        for book_id in book_ids:
            result = await collection.find_one({"douban_id": book_id})
            tmp_result = {}
            tmp_result.update(result)
            tmp_result["_id"] = str(result["_id"])
            tmp_result["stared"] = await check_stared(request, result["douban_id"])
            results_to_return.append(tmp_result)
        return json(results_to_return, headers={"Access-Control-Allow-Origin": "*"})  
    if query_field == "author":
        author_cursor = search_by_author(collection, query)
        results = await author_cursor.to_list(length=max_length)
        results_to_return = []
        for result in results:
            tmp_result = {}
            tmp_result.update(result)
            tmp_result["_id"] = str(result["_id"])
            tmp_result["stared"] = await check_stared(request, result["douban_id"])
            results_to_return.append(tmp_result)
        return json(results_to_return, headers={"Access-Control-Allow-Origin": "*"})
    if query_field == "title":
        title_cursor = search_by_title(collection, query)
        results = await title_cursor.to_list(length=max_length)
        results_to_return = []
        for result in results:
            tmp_result = {}
            tmp_result.update(result)
            tmp_result["_id"] = str(result["_id"])
            tmp_result["stared"] = await check_stared(request, result["douban_id"])
            results_to_return.append(tmp_result)
        return json(results_to_return, headers={"Access-Control-Allow-Origin": "*"})
        

@search.route("/autocomplete", methods=["GET", "POST"])
async def autocomplete(request):
    if request.method == "GET":
        query_field = request.args.get("field") if request.args.get("field") is not None else "all"
        query_type = request.args.get("type") if request.args.get("type") is not None else "match"
        source = request.args.get("source") if request.args.get("source") is not None else "100pdfs"
        query = request.args.get("query")
    else:
        query_field = request.data.get("field") if request.data.get("field") is not None else "all"
        query_type = request.data.get("type") if request.data.get("type") is not None else "match"
        source = request.data.get("source") if request.data.get("source") is not None else "100pdfs"
        query = request.data.get("query")
    print(source)
    print(type(source))
    searcher = PaperSearch() if source == "100pdfs" else PaperSearch("arxiv")
    search_fn = searcher.search_all_fields if query_field == "all" else searcher.search_specific_field
    if query_field not in ["all", "tag","ref_paper","conference","keywords","author","link","abstract","title","volume","journal","issn","publisher","doi"]:
        return text("not imply", status=416, headers={"Access-Control-Allow-Origin": "*"})
    query_size = 7
    # if request.query == None:
    #     return text("must request with a query", status=416, headers={"Access-Control-Allow-Origin": "*"})
    search_results = search_fn(query, query_field, query_size, query_type=query_type)
    # print(query_size)
    results = []
    i = 0
    for k, paper in search_results.items():
        # tem_results["_id"] = k
        # for key, value in paper.items():
        #     tem_results[key] = value
        # results[i] = tem_results
        results.append(paper[query_field if query_field != "all" else "title"][0])
        i += 1
    return json(results, headers={"Access-Control-Allow-Origin": "*"})