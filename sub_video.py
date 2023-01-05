from tempfile import NamedTemporaryFile
from logger import logger
import logging
import subprocess


def sub_video(video_file_path: str, sub_srt_str: str) -> bytes:
    subs_file = NamedTemporaryFile()
    video_out_file = NamedTemporaryFile(suffix='.mp4')
    with open(subs_file.name, "w") as f:
        f.write(sub_srt_str)
    cmd = f'ffmpeg -i {video_file_path} -vf subtitles={subs_file.name} -y {video_out_file.name}'
    logger.debug(f'ffmpeg command: "{cmd}"')
    logger.debug(f'ffmpeg command splitted: "{cmd.split(" ")}"')

    subprocess.check_call(cmd.split(" "))

    with open(video_out_file.name, "rb") as f:
        video_bytes = f.read()

    return video_bytes


if __name__ == '__main__':
    logging.basicConfig(level=logging.NOTSET)
    subs_str = open('subs.srt').read()
    video_path = 'speach_trim.mp4'
    video_dat = sub_video(video_path, subs_str)
    print(video_dat[:100])
