from db.database import Posts

Post = Posts()
    
async def add_post(user_id, text_post, photo_post, date_post):
    query = """
    INSERT INTO random_posts (
        user_id,
        text_post,
        photo_post,
        date_post
    ) VALUES ($1, $2, $3, $4)
    """
    
    try:
        pool = await Post.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, user_id, text_post, photo_post, date_post)
            return True
    except Exception as error:
        print(f"Ошибка добавление поста в БД: {error}")
        return False
    
async def select_post(user_id):
    query = """
    SELECT id, user_id, text_post, date_post
    FROM random_posts
    WHERE user_id = $1
    ORDER BY id DESC
    """
    
    try:
        pool = await Post.connect()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, user_id)
            return rows
    except Exception as error:
        print(f"Ошибка получения всех постов клиента: {error}")
        return None
    
async def delete_post_user(id_post, user_id):
    query = """
    DELETE FROM random_posts WHERE id = $1 AND user_id = $2
    """
    
    try:
        pool = await Post.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, id_post, user_id)
            return True
    except Exception as error:
        print(f"Ошибка удлаение поста в БД: {error}")
        return False
    
async def select_view_post_user(id_post, user_id):
    query = """
    SELECT text_post
    FROM random_posts
    WHERE user_id = $1 AND id = $2
    """
    
    try:
        pool = await Post.connect()
        async with pool.acquire() as conn:
            rows = await conn.fetchval(query, user_id, id_post)
            return rows
    except Exception as error:
        print(f"Ошибка получения поста клиента: {error}")
        return None