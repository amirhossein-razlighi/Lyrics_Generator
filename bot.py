from generator import LyricsGenerator
import logging
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    InlineQueryHandler,
)
import soundfile as sf
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv()

title = None
generator = LyricsGenerator()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to the lyrics generator bot, send me an audio file and I will generate lyrics for you",
    )


def process_audio(main_audio_path):
    global generator
    audio_chunks_paths = []
    audio, sample_rate = sf.read(main_audio_path)
    audio_duration = len(audio) / sample_rate
    print(audio_duration)
    if audio_duration > 30:
        # Split the audio into 30 seconds chunks
        for i in range(0, int(audio_duration), 30):
            audio_chunk = audio[i * sample_rate : (i + 30) * sample_rate]
            audio_chunk_path = f"audio_chunks_{i}.mp3"
            sf.write(audio_chunk_path, audio_chunk, sample_rate)
            audio_chunks_paths.append(audio_chunk_path)
    else:
        audio_chunks_paths.append(main_audio_path)
    for audio_chunk_path in audio_chunks_paths:
        yield generator.generate(audio_chunk_path)


async def get_audio_from_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global title
    audio = update.message.audio
    file_id = audio.file_id
    file_title = audio.title
    title = file_title
    file = await context.bot.get_file(file_id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Your music is being processed, please wait...",
    )
    await file.download_to_drive(custom_path=f"{file_title}.mp3")
    res = process_audio(title + ".mp3")
    if res:
        print(next(res))


if __name__ == "__main__":
    application = ApplicationBuilder().token(os.getenv("TOKEN")).build()
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)
    audio_handler = MessageHandler(filters.AUDIO, get_audio_from_user)
    application.add_handler(audio_handler)
    application.run_polling()
