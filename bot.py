import telebot
import sqlite3
import os
from typing import Optional
from config import BOT_TOKEN
bot = telebot.TeleBot(BOT_TOKEN)


DB_PATH = 'Films.sqlite'
IMG_FOLDER = 'img'


conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()


bot = telebot.TeleBot(BOT_TOKEN)

def get_movie_by_id(movie_id: int) -> Optional[tuple]:
    cursor.execute("SELECT ROWID, * FROM csv_file WHERE ROWID = ?", (movie_id,))
    return cursor.fetchone()

def get_random_movie() -> Optional[tuple]:
    cursor.execute("SELECT ROWID, * FROM csv_file ORDER BY RANDOM() LIMIT 1")
    return cursor.fetchone()

def get_movie_by_genre(genre: str) -> Optional[tuple]:
    cursor.execute("""
        SELECT ROWID, * FROM csv_file 
        WHERE genre LIKE ? 
        ORDER BY RANDOM() 
        LIMIT 1
    """, (f"%{genre}%",))
    return cursor.fetchone()

def format_movie(movie: tuple) -> str:
    movie_id = movie[0]
    title, year, certificate, duration, genre, rating, description, stars, votes = movie[1:]
    return (
        f"ID: {movie_id}\n"
        f"Название: {title}\n"
        f"Год: {year}\n"
        f"Рейтинг: {rating}\n"
        f"Жанр: {genre}\n"
        f"Описание: {description}\n"
        f"Актеры: {stars}\n"
        f"Голосов: {votes}"
    )

def get_image_path(movie_id: int) -> Optional[str]:
    img_number = movie_id % 100 or 100
    filename = f"{img_number}.jpg"
    img_path = os.path.join(IMG_FOLDER, filename)
    return img_path if os.path.exists(img_path) else None

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    genres = ['Action', 'Drama', 'Comedy', 'Horror', 'Fantasy', 'Crime', 'Adventure', 'Mystery', 'Thriller']
    markup.add(*genres)
    bot.send_message(
        message.chat.id,
        "Выберите жанр или используйте команды:\n"
        "/random - случайный фильм\n"
        "/help - помощь",
        reply_markup=markup
    )

@bot.message_handler(commands=['random'])
def random_movie(message):
    movie = get_random_movie()
    if movie:
        send_movie(message.chat.id, movie)
    else:
        bot.send_message(message.chat.id, "Фильмы не найдены")

@bot.message_handler(func=lambda message: True)
def genre_handler(message):
    genre = message.text
    movie = get_movie_by_genre(genre)
    if movie:
        send_movie(message.chat.id, movie)
    else:
        bot.send_message(
            message.chat.id, 
            f"Фильмы в жанре {genre} не найдены"
        )

def send_movie(chat_id: int, movie: tuple):
    try:
        caption = format_movie(movie)
        movie_id = movie[0]
        img_path = get_image_path(movie_id)
        
        if img_path:
            with open(img_path, 'rb') as photo:
                bot.send_photo(chat_id, photo, caption=caption)
        else:
            bot.send_message(chat_id, "Изображение не найдено\n\n" + caption)
    except Exception as e:
        bot.send_message(chat_id, f"Ошибка: {str(e)}\n\n{caption}")

if __name__ == "__main__":
    bot.polling(none_stop=True)