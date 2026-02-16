import telebot
from telebot import types
import configKeys
from pyowm import OWM
from pyowm.utils.config import get_default_config

# налаштування ОВМ для української мови
config_dict = get_default_config()
config_dict['language'] = 'uk'
owm = OWM(configKeys.WEATHER_API_KEY, config_dict)
mgr = owm.weather_manager()

# токен бота
bot = telebot.TeleBot(configKeys.BOT_TOKEN)

# меню з командами
def set_bot_commands():
    commands = [
        types.BotCommand("start", "Почати спілкування"),
        types.BotCommand("weather", "Погода сьогодні"),
        types.BotCommand("afterday", "Погода на завтра"),
        types.BotCommand("forecast3", "Погода на 3 дні"),
        types.BotCommand("forecast5", "Погода на 5 днів")
    ]
    bot.set_my_commands(commands)

set_bot_commands()

# --- ОБРОБКА КОМАНД ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Вітаю! Я погодний бот. Використовуй меню або команду /weather.")

@bot.message_handler(func=lambda message: message.text.lower() == "погода" or message.text.lower() == "погода сьогодні")
@bot.message_handler(commands=['weather'])
def weather_command(message):
    msg = bot.send_message(message.chat.id, "Будь ласка, введіть назву міста:")
    bot.register_next_step_handler(msg, get_weather)

@bot.message_handler(func=lambda message: message.text.lower() == "погода завтра")
@bot.message_handler(commands=['afterday'])
def weather_afterday_command(message):
    msg = bot.send_message(message.chat.id, "Будь ласка, введіть назву міста (на завтра):")
    bot.register_next_step_handler(msg, get_weather) # 

@bot.message_handler(commands=['forecast3', 'forecast5'])
def forecast_command(message):
    days = 3 if '3' in message.text else 5
    msg = bot.send_message(message.chat.id, f"Введіть місто для прогнозу на {days} днів:")
    bot.register_next_step_handler(msg, lambda m: get_forecast(m, days))

# --- ФУНКЦІЇ ЛОГІКИ ---

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
        
        weather_info = f"Погода в місті {city.capitalize()}:\n\n🌡️ Температура: {temperature}°C\n🤔 Відчувається як: {feels_like}°C\n💨 Вітер: {wind_speed} м/с\n💧 Вологість: {humidity}%\n🔽 Тиск: {pressure} hPa\n☁️ Стан: {description}"
        bot.send_message(message.chat.id, weather_info)
    except Exception as e:
        bot.send_message(message.chat.id, "😔 Не зміг знайти таке місто. Спробуйте ще раз.")

def get_forecast(message, days):
    try:
        city = message.text
        forecaster = mgr.forecast_at_place(city, '3h')
        forecast = forecaster.forecast
        
        res_text = f"📅 Прогноз у місті {city.capitalize()} на {days} днів:\n"
        last_date = None
        count = 0
        
        for weather in forecast:
            date_str = weather.reference_time('iso').split(' ')[0]
            if date_str != last_date and "12:00" in weather.reference_time('iso'):
                temp = weather.temperature('celsius')['temp']
                status = weather.detailed_status
                res_text += f"\n📆 {date_str}: {temp}°C, {status}"
                last_date = date_str
                count += 1
            if count >= days:
                break
        bot.send_message(message.chat.id, res_text)
    except Exception as e:
        bot.send_message(message.chat.id, "😔 Помилка прогнозу. Перевірте назву міста.")


@bot.message_handler(func=lambda message: True)
def handle_unknown_command(message):
    bot.send_message(message.chat.id, "Не зрозуміла команда. Введіть /weather")

if __name__ == '__main__':
    bot.polling(none_stop=True)