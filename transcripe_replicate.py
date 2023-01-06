import os
import logging
from logger import logger

import replicate
import asyncio


def transcribe_replicate_sync(file_path: str):
    whisper_model = os.environ.get('WHISPER_MODEL') if os.environ.get('WHISPER_MODEL') is not None else "large"  # go all in per default
    logger.info(f'We use model "{whisper_model}"')

    model = replicate.models.get("openai/whisper")
    version = model.versions.get("30414ee7c4fffc37e260fcab7842b5be470b9b840f2b608f5baa9bbef9a259ed")  # latest as of 05.01.2023
    with open(file_path, "rb") as f:
        prediction = version.predict(audio=f, model=whisper_model)
    # be compatible with local computation
    prediction['language'] = prediction['detected_language']
    prediction['text'] = prediction['transcription']
    return prediction


async def transcribe_replicate(file_path: str):
    return await asyncio.get_event_loop().run_in_executor(None, transcribe_replicate_sync, file_path)


if __name__ == '__main__':
    logging.basicConfig(level=logging.NOTSET)
    path = 'speach_trim.mp4'
    res = transcribe_replicate_sync(path)
    print(res)
