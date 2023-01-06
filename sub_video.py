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


def sub_audio(audio_file_path: str, sub_srt_str: str) -> bytes:
    subs_file = NamedTemporaryFile()
    video_out_file = NamedTemporaryFile(suffix='.mp4')
    with open(subs_file.name, "w") as f:
        f.write(sub_srt_str)
    cmd = f"ffmpeg -f lavfi -i color=c=black:s=1280x720:r=5 -i {audio_file_path} -crf 0 -c:a copy -shortest -vf " \
          f"subtitles={subs_file.name}:force_style='Fontsize=24' -y {video_out_file.name}"
    logger.debug(f'ffmpeg audio command: "{cmd}"')
    logger.debug(f'ffmpeg audio command splitted: "{cmd.split(" ")}"')

    subprocess.check_call(cmd.split(" "))

    with open(video_out_file.name, "rb") as f:
        video_bytes = f.read()

    return video_bytes


def get_all_codec_types(file_path: str) -> [str]:
    """
    Returns a list of strings.
    Each string in the list is 'audio' or 'video' or possibly something else ...?
    This list can be empty.
    """
    cmd_str = f"ffprobe -loglevel error -show_entries stream=codec_type -of csv=p=0 {file_path}"
    try:
        output = subprocess.check_output(cmd_str.split(" "), encoding='utf8')
    except subprocess.CalledProcessError:  # in this case it is probably not a multimedia file
        return []
    return output.split("\n")[:-1]


if __name__ == '__main__':
    logging.basicConfig(level=logging.NOTSET)
    subs_str = open('subs.srt').read()
    video_path = 'speach_trim.mp4'

    print(get_all_codec_types('sub_video.py'))
    print(get_all_codec_types(video_path))

    video_dat = sub_video(video_path, subs_str)

    print(video_dat[:100])
