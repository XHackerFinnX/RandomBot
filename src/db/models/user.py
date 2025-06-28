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
    

async def update_user(
    user_id: int, username: str, first_name: str, last_name: str, entry_date
):
    query = """
    UPDATE random_user
    SET
        username = $1,
        first_name = $2,
        last_name = $3,
        entry_date = $4
    WHERE
        user_id = $5
    """
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(
                query, username, first_name, last_name, entry_date, user_id
            )
    except Exception as error:
        print(f"Ошибка при обновлении клиента в БД: {error}")
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
    
async def select_photo_post(user_id, post_text):
    query = """
    SELECT photo_post FROM random_posts
    WHERE user_id = $1 AND text_post = $2
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            post_photo = await conn.fetchval(query, user_id, post_text)
            return post_photo
    except Exception as error:
        print(f"Ошибка получения фотографии для поста из random_posts: {error}")
        return None
    
async def select_raffle_active_my(user_id):
    query = """
    SELECT raffle_id, name, start_date, end_date, status FROM random_raffle
    WHERE user_id = $1 AND status = 'Активен'
    ORDER BY status = 'Активен' DESC, start_date DESC
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            user_raffle_my = await conn.fetch(query, user_id)
            return user_raffle_my
    except Exception as error:
        print(f"Ошибка получения активных розыгрышей: {error}")
        return None
    
async def select_raffle_expectation_my(user_id):
    query = """
    SELECT raffle_id, name, start_date, end_date, status FROM random_raffle
    WHERE user_id = $1 AND status = 'Ожидание'
    ORDER BY status = 'Ожидание' DESC, start_date DESC
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            user_raffle_my = await conn.fetch(query, user_id)
            return user_raffle_my
    except Exception as error:
        print(f"Ошибка получения ожидающих розыгрышей: {error}")
        return None
    
async def select_raffle_completed_my(user_id):
    query = """
    SELECT raffle_id, name, start_date, end_date, status FROM random_raffle
    WHERE user_id = $1 AND status = 'Завершен'
    ORDER BY status = 'Завершен' DESC, start_date DESC
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            user_raffle_my = await conn.fetch(query, user_id)
            return user_raffle_my
    except Exception as error:
        print(f"Ошибка получения завершенных розыгрышей: {error}")
        return None
    
async def select_raffle_participating(user_id, status):
    query = """
    SELECT DISTINCT ON (rut.raffle_id) 
        rut.raffle_id, 
        rr.name, 
        rr.start_date,
        rr.end_date, 
        rr.status
    FROM random_user_turn AS rut
    LEFT JOIN random_raffle AS rr
        ON rut.raffle_id = rr.raffle_id
    WHERE rut.user_id = $1
        AND rr.status = $2
    ORDER BY rut.raffle_id, rr.start_date DESC;
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            user_raffle = await conn.fetch(query, user_id, status)
            return user_raffle
    except Exception as error:
        print(f"Ошибка получения активных розыгрышей участвовшего пользователя: {error}")
        return None
    
async def update_cancel_raffle(raffle_id):
    query = """
    UPDATE random_raffle
    SET status = 'Отмена'
    WHERE raffle_id = $1
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, raffle_id)
    except Exception as error:
        print(f"Ошибка отмены розыгрыша: {error}")
        
async def update_status_raffle_start(raffle_id):
    query = """
    UPDATE random_raffle
    SET status = 'Активен'
    WHERE raffle_id = $1
    """
    
    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, raffle_id)
    except Exception as error:
        print(f"Ошибка запуска розыгрыша через настройки: {error}")
        

async def check_user_save_raffle(user_id):
    query = """
    SELECT 1 FROM random_raffle_save WHERE user_id = $1
    """

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            result = await conn.fetchrow(query, user_id)
            return bool(result)
    except Exception as error:
        print(f"Ошибка получения сохраненного розыгрыша: {error}")
        return False


async def update_save_raffle(
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
    user_win,
    step
):
    query = """
    UPDATE random_raffle_save
    SET
        name = $1,
        post_id = $2,
        post_text = $3,
        post_button = $4,
        sub_channel_id = $5,
        announcet_channel_id = $6,
        results_channel_id = $7,
        start_date = $8,
        end_date = $9,
        user_winners = $10,
        step = $11
    WHERE user_id = $12;
    """

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(
                query,
                name,
                post_id,
                post_text,
                post_button,
                sub_channel_id,
                announcet_channel_id,
                results_channel_id,
                start_date,
                end_date,
                user_win,
                step,
                user_id
            )
            return True
    except Exception as error:
        print(f"Ошибка при обновлении розыгрыша: {error}")
        return False
    

async def update_save_raffle_end_date(
    user_id,
    name,
    post_id,
    post_text,
    post_button,
    sub_channel_id,
    announcet_channel_id,
    results_channel_id,
    start_date,
    user_win,
    step
):
    query = """
    UPDATE random_raffle_save
    SET
        name = $1,
        post_id = $2,
        post_text = $3,
        post_button = $4,
        sub_channel_id = $5,
        announcet_channel_id = $6,
        results_channel_id = $7,
        start_date = $8,
        user_winners = $9,
        step = $10
    WHERE user_id = $11;
    """

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(
                query,
                name,
                post_id,
                post_text,
                post_button,
                sub_channel_id,
                announcet_channel_id,
                results_channel_id,
                start_date,
                user_win,
                step,
                user_id
            )
            return True
    except Exception as error:
        print(f"Ошибка при обновлении розыгрыша: {error}")
        return False


async def add_save_raffle(
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
    user_win,
    step
):
    query = """
    INSERT INTO random_raffle_save (
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
        step
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
    );
    """

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(
                query,
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
                user_win,
                step
            )
            return True
    except Exception as error:
        print(f"Ошибка при сохранении розыгрыша: {error}")
        return False
    

async def select_all_save_raffle(user_id):
    query = """
    SELECT * FROM random_raffle_save
    WHERE user_id = $1
    """

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            record = await conn.fetchrow(query, user_id)
            return dict(record) if record else None
    except Exception as error:
        print(f"Ошибка при получении сохраненнго розыгрыша: {error}")
        return None
    
async def delete_save_raffle(user_id):
    query = """
    DELETE FROM random_raffle_save
    WHERE user_id = $1
    """

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            await conn.execute(query, user_id)
            return True
    except Exception as error:
        print(f"Ошибка при удалении сохраненного розыгрыша: {error}")
        return False
    

async def select_channel_save_raffle(user_id):
    query = """
    SELECT sub_channel_id FROM random_raffle_save
    WHERE user_id = $1
    """

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            record = await conn.fetch(query, user_id)
            return record[0]
    except Exception as error:
        print(f"Ошибка при получении каналов сохраненного розыгрыша: {error}")
        return None
    

async def select_all_raffle_active():
    query = """
    SELECT raffle_id, name, post_text FROM random_raffle
    WHERE status = 'Активен'
    """

    try:
        pool = await User.connect()
        async with pool.acquire() as conn:
            record = await conn.fetch(query)
            return record
    except Exception as error:
        print(f"Ошибка при всех розыгрышей которые сейчас активные: {error}")
        return None