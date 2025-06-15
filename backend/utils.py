import motor
from config import MONGODB_CONNECTION_STRING
from typing import Dict, Any
from datetime import datetime
from auth import *

def get_collection(source):
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
    if source == 'books':
        return client.book[source]
    elif source == 'authors':
        return client.book[source]
    else:
        raise ValueError("Invalid source.")

def parse_reading_history(reading_history: Dict[str, Any]) -> Dict[str, Any]:
    """
    解析阅读历史，将其转换为前端友好且可JSON序列化的格式
    
    Args:
        reading_history: 包含阅读历史数据的字典，格式为 {douban_id: [click_count, datetime_obj], ...}
        
    Returns:
        转换后的阅读历史字典，datetime 被转换为 "YYYY-MM-DD HH:MM:SS" 格式的字符串
    """
    parsed_history = {}
    
    if not reading_history:
        return parsed_history
    
    for book_id, history_data in reading_history.items():
        if len(history_data) >= 2:
            click_count = history_data[0]
            timestamp = history_data[1]
            
            # 检查时间戳是否是 datetime 类型
            if isinstance(timestamp, datetime):
                # 将 datetime 转换为 "YYYY-MM-DD HH:MM:SS" 格式
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # 如果不是 datetime 类型，尝试保留原值或设置为默认值
                formatted_time = str(timestamp)
            
            # 保存转换后的数据，确保可以 JSON 序列化
            parsed_history[book_id] = {
                "count": click_count,
                "last_read": formatted_time
            }
    
    return parsed_history


async def check_stared(request, douban_id):
    """
    检查当前登录用户是否已收藏了特定的书籍
    
    参数:
        request: Sanic请求对象
        books_collection: 书籍集合的引用
    
    返回:
        bool: 如果用户已收藏该书籍返回True，否则返回False
    """
    is_authenticated, username = await check_login(request)
    if not is_authenticated:
        return False
    
    # 连接数据库
    db = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
    client = db['book']
    users_collection = client['users']
    
    # 获取用户信息
    user = await users_collection.find_one({"username": username})
    if not user:
        return False
    
    # 方法1: 检查用户的star_list中是否包含该书籍
    star_list = user.get("star_list", [])
    if douban_id in star_list:
        return True
    
    # 方法2: 检查书籍的stared_by列表中是否包含该用户
    # 这是双重验证，理论上方法1已足够，但为了确保数据一致性，可同时检查
    # book = await books_collection.find_one({"douban_id": douban_id})
    # if book and "stared_by" in book and user_id in book.get("stared_by", []):
    #     return True
        
    return False