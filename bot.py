import telebot
import configKeys
from pyowm import OWM
from pyowm.utils.config import get_default_config


config_dict = get_default_config()
config_dict['language'] = 'uk'
owm = OWM(configKeys.WEATHER_API_KEY, config_dict)
bot = telebot.TeleBot(configKeys.BOT_TOKEN)  
mgr = owm.weather_manager()
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вітаю! Я - бот який може надати інформацію про погоду. Введіть команду /weather, щоб дізнатися погоду в вашому місті.")


@bot.message_handler(func=lambda message: message.text.lower() == "погода сьогодні")
@bot.message_handler(commands=['weather'])
def weather_command(message):
    msg = bot.send_message(message.chat.id, "Будь ласка, введіть назву міста:")
    bot.register_next_step_handler(msg, get_weather)

@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    bot.send_message(message.chat.id, "Не зрозуміла команда. Введіть команду /weather")

def get_weather(message):
    try:
        city = message.text
        observation = mgr.weather_at_place(city)
        weather = observation.weather
        
        temperature = weather.temperature('celsius')['temp']
        feels_like = weather.temperature('celsius')['feels_like']
        pressure = weather.pressure['press']
        humidity = weather.humidity
        wind_speed = weather.wind()['speed']
        description = weather.detailed_status
        
        weather_info = f"""
Погода в місті {city}:
        
🌡️ Температура: {temperature}°C
🤔 Відчувається як: {feels_like}°C
💨 Вітер: {wind_speed} м/с
💧 Вологість: {humidity}%
🔽 Тиск: {pressure} hPa
☁️ Стан: {description}
"""
        bot.send_message(message.chat.id, weather_info)
    except Exception as e:
        bot.send_message(message.chat.id, "😔 На жаль, не змогу знайти місто. Спробуйте ще раз.")
bot.polling(none_stop=True)
