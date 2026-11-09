import asyncio
import logging
import re
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    LabeledPrice,
    PreCheckoutQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

# ⚠️ ВСТАВЬТЕ СЮДА ВАШ СВЕЖИЙ ТОКЕН ИЗ BOTFATHER (Кавычки не удалять!)
TOKEN = "8957653429:AAFNhZXXoeGd_7g_EVaBRQPoa4g6n5AUmKo"

# ID вашего закрытого приватного канала (куда дается доступ после оплаты)
CHANNEL_ID = -1004288240193

# Цена доступа в Telegram Stars
PRICE_IN_STARS = 100

# 🔗 ПРОСТО ВСТАВЬТЕ СЮДА ПОЛНУЮ ССЫЛКУ НА GOOGLE ДИСК (Кавычки не удалять!)
GOOGLE_DRIVE_URL = "https://drive.google.com/file/d/1DVDs3X0vTMTflBuOogaNZWSIm2WAXNFm/view?usp=drivesdk"


# Функция для автоматического создания прямой ссылки из обычной ссылки Google Drive
def get_direct_google_drive_link(url: str) -> str:
    match = re.search(r"/d/([a-zA-Z0-9_-]{33,})", url)
    if match:
        file_id = match.group(1)
        return f"https://google.com{file_id}"
    return url


# Генерируем прямую ссылку для видео-плеера
VIDEO_SOURCE = get_direct_google_drive_link(GOOGLE_DRIVE_URL)

dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Посмотреть промо-видео", url=GOOGLE_DRIVE_URL)],
        [InlineKeyboardButton(text=f"⭐ Купить доступ за {PRICE_IN_STARS} звёзд", callback_data="buy_access")]
    ])
    
    welcome_text = (
        "👋 <b>Привет! Рады видеть тебя!</b>\n\n"
        "Чтобы узнать, какой эксклюзивный контент тебя ждет в нашем закрытом канале, "
        "обязательно посмотри наше короткое промо-видео.\n\n"
        "Нажми на кнопку <b>«🎬 Посмотреть промо-видео»</b> ниже, а затем возвращайся сюда, "
        "чтобы оплатить подписку с помощью Telegram Stars и получить свою персональную ссылку-приглашение!"
    )
    
    try:
        await bot.send_video(
            chat_id=message.chat.id,
            video=VIDEO_SOURCE,
            caption=welcome_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка отправки видео: {e}")
        await message.answer(
            text=welcome_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

@dp.callback_query(F.data == "buy_access")
async def process_buy(callback_query: CallbackQuery, bot: Bot):
    try:
        await bot.send_invoice(
            chat_id=callback_query.from_user.id,
            title="Доступ в закрытый Telegram-канал",
            description="Эксклюзивный доступ к нашему закрытому сообществу.",
            payload="channel_access_payload",
            currency="XTR",
            prices=[LabeledPrice(label="Stars", amount=PRICE_IN_STARS)]
        )
        await callback_query.answer()
    except Exception as e:
        logging.error(f"Ошибка при выставлении счета: {e}")
        await callback_query.answer("Произошла ошибка при формировании оплаты.", show_alert=True)

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 🔄 МОДЕРНИЗИРОВАННЫЙ ОБРАБОТЧИК ОПЛАТЫ: Теперь выдает красивую большую кнопку
@dp.message(F.successful_payment)
async def success_payment_handler(message: Message, bot: Bot):
    try:
        # Создаем одноразовую ссылку для вступления
        invite_link = await bot.create_chat_invite_link(chat_id=CHANNEL_ID, member_limit=1)
        
        # Оформляем ссылку в виде большой кнопки, которую невозможно пропустить
        success_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Вступить в закрытый канал", url=invite_link.invite_link)]
        ])
        
        await message.answer(
            "🎉 <b>Оплата прошла успешно! Спасибо за покупку!</b>\n\n"
            "Ваша персональная ссылка готова. Нажмите на зелёную кнопку ниже, чтобы войти в канал.\n\n"
            "⚠️ <i>Внимание: кнопка сработает только один раз. Пожалуйста, сразу нажмите «Вступить» в открывшемся окне.</i>",
            reply_markup=success_keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Ошибка создания ссылки: {e}")
        await message.answer(
            f"❌ Произошла техническая ошибка при генерации ссылки. "
            f"Пожалуйста, свяжитесь с администратором. Код ошибки: {e}"
        )

async def main():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот успешно запущен и ожидает оплат...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nБот остановлен вручную.")
    except Exception as fatal_error:
        print("\n" + "="*50)
        print("❌ БОТ УПАЛ С КРИТИЧЕСКОЙ ОШИБКОЙ:")
        print("="*50)
        import traceback
        traceback.print_exc()
        print("="*50)
        input("\nНажмите ENTER, чтобы закрыть это окно...")
