import logging
import os
import pathlib
import time

import telegram
import whisper
from subtitles import generate_srt, generate_vtt
from pydub import AudioSegment
from telegram import Update
from telegram.ext import MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes

from filter_allowed_chats import FilterAllowedChats
from logger import logger


def create_project_folder():
    pathlib.Path(file_download_path).mkdir(exist_ok=True)


async def escape_markdown_chars(text: str) -> str:
    temporal = text
    for char in escaping_chars:
        temporal = temporal.replace(char, f"\\{char}")
    return temporal


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="From now on I'll transcribe your audio messages in this group chat"
    )


async def convert_ogg_to_mp3(ogg_file_path, mp3_file_path):
    given_audio = AudioSegment.from_file(ogg_file_path, format="ogg")
    given_audio.export(mp3_file_path, format="mp3")


async def set_typing_in_chat(context, effective_chat_id):
    await context.bot.send_chat_action(chat_id=effective_chat_id, action=telegram.constants.ChatAction.TYPING)


async def get_as_markdown(text, processing_time):
    transcription = text["text"].removeprefix(" ")
    language_ = text["language"]
    markdown_message = '''\
Detected language: {language}
Processing time: {processing_time}s
Transcription:
```
{transcription}
```
        '''.format(transcription=transcription, language=language_, processing_time=int(processing_time))
    escaped_markdown_message = await escape_markdown_chars(markdown_message)
    return escaped_markdown_message


async def download_voice_message(context, file_id, mp3_audio_path, ogg_audio_path):
    new_file = await context.bot.get_file(file_id)
    await new_file.download_to_drive(custom_path=ogg_audio_path)
    await convert_ogg_to_mp3(ogg_audio_path, mp3_audio_path)


async def transcribe_audio(mp3_audio_path):
    audio = whisper.load_audio(mp3_audio_path)
    result = model.transcribe(audio)
    return result


async def process_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    effective_chat_id = update.effective_chat.id
    message_id = update.message.message_id
    if update.message.voice:
        file_unique_id = update.message.voice.file_unique_id
        file_id = update.message.voice.file_id
    elif update.message.audio:
        file_unique_id = update.message.audio.file_unique_id
        file_id = update.message.audio.file_id
    elif update.message.video:
        file_unique_id = update.message.video.file_unique_id
        file_id = update.message.video.file_id
    else:
        logger.warning('Message is not a video, not an audio, not a voice.')
        await context.bot.send_message(
            chat_id=effective_chat_id,
            text='Your message is not a video, not an audio, not a voice. I can not handle it',
            reply_to_message_id=message_id,
        )
        return

    try:
        start_time = time.time()
        logger.debug("Voice message received")
        await set_typing_in_chat(context, effective_chat_id)
        path = await (await context.bot.get_file(file_id)).download_to_drive()
        result = await transcribe_audio(path)

        # generate srt and vtt
        srt_str = generate_srt(result["segments"])
        vtt_str = generate_vtt(result["segments"])

        final_time = time.time()
        processing_time = (final_time - start_time)

        response_message = await get_as_markdown(result, processing_time)
        await context.bot.send_message(
            chat_id=effective_chat_id, text=response_message, reply_to_message_id=message_id,
            parse_mode=telegram.constants.ParseMode.MARKDOWN_V2
        )
        await context.bot.send_message(
            chat_id=effective_chat_id,
            text="Additionally you can find subtitle files in the following attachments."
        )
        await context.bot.send_document(effective_chat_id, srt_str.encode(), filename='subs.srt')
        await context.bot.send_document(effective_chat_id, vtt_str.encode(), filename='subs.vtt')

    except Exception as e:
        error_message = f"Error converting video to audio. Exception={e}"
        await context.bot.send_message(chat_id=effective_chat_id, text=error_message, reply_to_message_id=message_id)
        pass
    finally:
        os.remove(path)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.NOTSET
)

bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
allowed_chat_ids = os.environ.get("ALLOWED_CHAT_IDS", default="").split(",")
file_download_path = "/tmp/whispering-for-chaos"
device = os.environ.get("WHISPER_DEVICE", default="cpu")
whisper_model = os.environ.get("WHISPER_MODEL", default="large")
escaping_chars = ['_', '*', '[', ']', '(', ')', '~', '>', '+', '-', '=', '|', '{', '}', '.', '!']
logger.info(f"configuration: device={device}, whisper_model={whisper_model} allowed_chat_ids={allowed_chat_ids}")
logger.info(f"Up to load whisper model, this might take a bit")
model = whisper.load_model(whisper_model, device=device)
logger.info(f"Finished loading the whisper model")


create_project_folder()
application = ApplicationBuilder().token(bot_token).build()

start_handler = CommandHandler('start', start)
filter_allowed_chats = FilterAllowedChats(allowed_chat_ids)
audio_message_handler = MessageHandler(filter_allowed_chats, process_voice_message)

application.add_handler(start_handler)
application.add_handler(audio_message_handler)

application.run_polling()
