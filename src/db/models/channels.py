from db.database import Channels

Channel = Channels()

async def check_channel(user_id, channel_id):
    query = """
    SELECT channel_id
    FROM random_channels
    WHERE user_id = $1 AND channel_id = $2
    """
    
    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            channel = await conn.fetch(query, user_id, channel_id)
            return channel
    except Exception as error:
        print(f"Ошибка получения channel клиента: {error}")
        return None

async def add_channel(user_id, channel_id, channel_subscribers, channel_name, channel_photo, channel_tg):
    query = """
    INSERT INTO random_channels (
        user_id,
        channel_id,
        channel_subscribers,
        channel_name,
        channel_photo,
        channel_status,
        channel_tg
    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    
    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, user_id, channel_id, channel_subscribers, channel_name, channel_photo, True, channel_tg)
    except Exception as error:
        print(f"Ошибка добавление канала в БД: {error}")
        
async def update_channel(user_id, channel_id, channel_subscribers, channel_name, channel_photo, channel_status, channel_tg):
    query = """
    UPDATE random_channels
    SET (channel_subscribers, channel_name, channel_photo, channel_status, channel_tg) = ($1, $2, $3, $4, $5)
    WHERE user_id = $6 AND channel_id = $7
    """
    
    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, channel_subscribers, channel_name, channel_photo, channel_status, channel_tg, user_id, channel_id)
    except Exception as error:
        print(f"Ошибка обновления в БД канала: {error}")
        
async def update_channel_false(user_id, channel_id, channel_status):
    query = """
    UPDATE random_channels
    SET channel_status = $1
    WHERE user_id = $2 AND channel_id = $3
    """
    
    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, channel_status, user_id, channel_id)
    except Exception as error:
        print(f"Ошибка обновления в БД: {error}")
        
async def select_channel(user_id):
    query = """
    SELECT channel_id, channel_name, channel_subscribers, channel_photo, channel_status, user_id
    FROM random_channels
    WHERE user_id = $1
    """

    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, user_id)
            return rows
    except Exception as error:
        print(f"Ошибка получения всех channel клиента: {error}")
        return None
    
async def select_channel_true(user_id):
    query = """
    SELECT channel_id, channel_name, channel_subscribers, channel_photo, channel_status, user_id
    FROM random_channels
    WHERE user_id = $1 AND channel_status = true
    """

    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, user_id)
            return rows
    except Exception as error:
        print(f"Ошибка получения всех channel клиента: {error}")
        return None
    
async def delete_channel_user(user_id, id_channel):
    query = """
    DELETE FROM random_channels WHERE channel_id = $1 AND user_id = $2
    """
    
    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, id_channel, user_id)
            return True
    except Exception as error:
        print(f"Ошибка удлаение канала в БД: {error}")
        return False
    
async def check_channel_user_sub(channel_tg: str):
    query ="""
    SELECT channel_id, channel_name, channel_subscribers, channel_photo, channel_status, user_id
    FROM random_channels
    WHERE channel_tg = $1 AND channel_status = true
    """
    
    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, channel_tg)
            return rows
    except Exception as error:
        print(f"Ошибка получения channel по tg: {error}")
        return None
    
async def check_channel_id_sub(channel_id: int):
    query ="""
    SELECT channel_id, channel_name, channel_subscribers, channel_photo, channel_status, user_id, channel_tg
    FROM random_channels
    WHERE channel_id = $1 AND channel_status = true
    """
    
    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, channel_id)
            return rows
    except Exception as error:
        print(f"Ошибка получения channel по id: {error}")
        return None
    
async def select_tgname_channel(channel_id):
    query = """
    SELECT channel_tg
    FROM random_channels
    WHERE channel_id = $1 AND channel_status = true
    """
    
    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            rows = await conn.fetchval(query, channel_id)
            return rows
    except Exception as error:
        print(f"Ошибка получения channel: {error}")
        return None
    
async def select_active_raffle(status):

    query = """
    SELECT raffle_id, start_date, end_date
    FROM random_raffle
    WHERE status = $1
    """
    
    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, status)
            return rows
    except Exception as error:
        print(f"Ошибка получения всех розыгрышей для старта: {error}")
        return None
    
async def select_send_channel_result(hash_id):
    query = """
    SELECT results_channel_id
    FROM random_raffle
    WHERE raffle_id = $1
    """
    
    try:
        pool = await Channel.connect()
        async with pool.acquire() as conn:
            rows = await conn.fetchval(query, hash_id)
            return rows
    except Exception as error:
        print(f"Ошибка получения каналов для результатов: {error}")
        return None