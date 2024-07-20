import sqlite3
import random
from datetime import datetime

conn = sqlite3.connect('../instance/database.db')
c = conn.cursor()

post_count = 10

for i in range(post_count):
    user_id = 1
    isGroup = random.choice([None, '1'])
    text = f'Тестовый пост {i + 1}'
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    likes = random.randint(1, 1000)
    comments = 0

    # Обработка None для isGroup
    if isGroup is not None:
        isGroup = f"'{isGroup}'"
    else:
        isGroup = 'NULL'

    c.execute(
        f'INSERT into "post"(user_id, isGroup, text, date, likes, comments) VALUES ({user_id}, {isGroup}, "{text}", "{date}", {likes}, {comments})')
    conn.commit()

print(f'Создано {post_count} записей')
