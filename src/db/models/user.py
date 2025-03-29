from db.database import User

User = User()


async def check_user(user_id: int):
    query = "SELECT user_id FROM random_user WHERE user_id = $1"

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            users = await conn.fetch(query, user_id)
            return users
    except Exception as error:
        print(f"Ошибка получения id клиента: {error}")
        return None


async def add_user(
    user_id: int, username: str, first_name: str, last_name: str, entry_date
):
    query = """
    INSERT INTO random_user (
        user_id,
        username,
        first_name,
        last_name,
        entry_date
    ) VALUES ($1, $2, $3, $4, $5)
    """
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(
                query, user_id, username, first_name, last_name, entry_date
            )
    except Exception as error:
        print(f"Ошибка добавление клиента в БД: {error}")
        return None


async def add_raffle(
    raffle_id,
    user_id,
    name,
    post_id,
    post_text,
    post_button,
    sub_channel_id,
    announcet_channel_id,
    results_channel_id,
    start_date,
    end_date,
    user_winners,
    status
):
    query = """
    INSERT INTO random_raffle (
        raffle_id,
        user_id,
        name,
        post_id,
        post_text,
        post_button,
        sub_channel_id,
        announcet_channel_id,
        results_channel_id,
        start_date,
        end_date,
        user_winners,
        status
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
    """

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(
                query,
                raffle_id,
                user_id,
                name,
                post_id,
                post_text,
                post_button,
                sub_channel_id,
                announcet_channel_id,
                results_channel_id,
                start_date,
                end_date,
                user_winners,
                status
            )
    except Exception as error:
        print(f"Ошибка добавление розыгрыша в БД: {error}")
        return None
    
async def add_channel_send(raffle_id, send_channel):
    query = """
    INSERT INTO random_send_raffle (
        raffle_id,
        channel_send
    ) VALUES ($1, $2)
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, raffle_id, send_channel)
    except Exception as error:
        print(f"Ошибка добавление id сообщения канала в БД: {error}")
        return None
    
async def select_channel_send(raffle_id):
    query = """
    SELECT channel_send
    FROM random_send_raffle
    WHERE raffle_id = $1
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            channel_send = await conn.fetch(query, raffle_id)
            return channel_send
    except Exception as error:
        print(f"Ошибка получения send_channel: {error}")
        return None
    
async def count_user_sub_channel(raffle_id):
    query = """
    SELECT COUNT(user_id)
    FROM random_user_turn
    WHERE raffle_id = $1
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            user_count = await conn.fetch(query, raffle_id)
            return user_count
    except Exception as error:
        print(f"Ошибка получения количества пользователей: {error}")
        return None
    
    
async def add_user_raffle(hash_id, user_id):
    query = """
    INSERT INTO random_user_turn (
        raffle_id,
        user_id
    ) VALUES ($1, $2)
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, hash_id, user_id)
    except Exception as error:
        print(f"Ошибка добавления пользователя в розыгрыш в БД: {error}")
        return None
    
async def delete_user_raffle(hash_id, user_id):
    query = """
    DELETE FROM random_user_turn WHERE raffle_id = $1 AND user_id = $2
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, hash_id, user_id)
    except Exception as error:
        print(f"Ошибка удаления пользователя в розыгрыш в БД: {error}")
        return None
    
async def check_user_raffle(hash_id, user_id):
    query = """
    SELECT user_id 
    FROM random_user_turn
    WHERE raffle_id = $1 AND user_id = $2
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            user_id = await conn.fetch(query, hash_id, user_id)
            return user_id
    except Exception as error:
        print(f"Ошибка проверки пользователя на подписки: {error}")
        return None
    
async def check_hash_id_raffle(hash_id):
    query = """
    SELECT raffle_id
    FROM random_raffle
    WHERE raffle_id = $1
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            raffle_id = await conn.fetch(query, hash_id)
            return raffle_id
    except Exception as error:
        print(f"Ошибка получения id розыгрыша: {error}")
        return None
    
async def select_raffle_data(hash_id):
    query = """
    SELECT *
    FROM random_raffle
    WHERE raffle_id = $1
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            raffle = await conn.fetch(query, hash_id)
            return raffle
    except Exception as error:
        print(f"Ошибка получения информации о розыгрыше: {error}")
        return None
    
async def update_raffle_end(hash_id, text_status):
    query = """
    UPDATE random_raffle
    SET status = $1
    WHERE raffle_id = $2
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, text_status, hash_id)
    except Exception as error:
        print(f"Ошибка обновления статуса розыгрыша: {error}")
        
        
async def select_all_user_raffle(raffle_id):
    query = """
    SELECT user_id
    FROM random_user_turn
    WHERE raffle_id = $1
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            all_user = await conn.fetch(query, raffle_id)
            return all_user
    except Exception as error:
        print(f"Ошибка получения все пользователей в розыгрыше: {error}")
        return None
    
    
async def select_turn_user_raffle(raffle_id):
    query = """
    SELECT user_id
    FROM random_user_turn
    WHERE raffle_id = $1 AND turn = true
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            turn_user = await conn.fetch(query, raffle_id)
            return turn_user
    except Exception as error:
        print(f"Ошибка получения гарантированного победителя: {error}")
        return None
    
async def add_raffle_archive(raffle_id, winner, start_date, end_date):
    query = """
    INSERT INTO random_raffle_archive (
        raffle_id, winner, start_date, end_date
    ) VALUES ($1, $2, $3, $4)
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, raffle_id, winner, start_date, end_date)
    except Exception as error:
        print(f"Ошибка добавления розыграша победителей в архив: {error}")
        
async def select_winner_raffle_archive(raffle_id):
    query = """
    SELECT winner
    FROM random_raffle_archive WHERE raffle_id = $1
    """

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            winner_user = await conn.fetchval(query, raffle_id)
            return winner_user
    except Exception as error:
        print(f"Ошибка получения список победителей {raffle_id}: {error}")
        return None
        
async def winner_user(user_id: int):
    query = "SELECT username FROM random_user WHERE user_id = $1"

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            users = await conn.fetchval(query, user_id)
            return users
    except Exception as error:
        print(f"Ошибка получения username клиента: {error}")
        return None
    
async def update_winuser(hash_id, user_id):
    query = """
    UPDATE random_user_turn
    SET turn = true
    WHERE raffle_id = $1 AND user_id = $2
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, hash_id, user_id)
    except Exception as error:
        print(f"Ошибка обновления подкрутки: {error}")
        
async def select_photo_raffle(hash_id):
    query = """
    SELECT photo_post FROM (
	    SELECT rr.raffle_id, rp.photo_post
	    FROM random_raffle AS rr
	    JOIN random_posts AS rp
	    ON rr.post_text = rp.text_post AND rr.user_id = rp.user_id
    )
    WHERE raffle_id = $1
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            post_photo = await conn.fetchval(query, hash_id)
            return post_photo
    except Exception as error:
        print(f"Ошибка получения фотографии для поста: {error}")
        return None