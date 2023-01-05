from typing import Iterator

from whisper.utils import write_srt, write_vtt
from tempfile import NamedTemporaryFile

TEST_STR = '{"text": " City is true of Germany. Real, lasting peace in Europe can never be assured as long as one German out of four is denied the elementary right of free men and that is to make a free choice in 18 years of peace and good faith. This generation of Germans has earned the right to be free, including the right to unite their families and their needs in lasting peace with good will to all people. You live in a defender dial in the freedom, but your life.", "segments": [{"id": 0, "seek": 0, "start": 0.0, "end": 3.24, "text": " City is true of Germany.", "tokens": [2254, 318, 2081, 286, 4486, 13], "temperature": 0.0, "avg_logprob": -0.38270172706017125, "compression_ratio": 1.4055944055944056, "no_speech_prob": 0.03617946431040764}, {"id": 1, "seek": 0, "start": 3.24, "end": 14.76, "text": " Real, lasting peace in Europe can never be assured as long as one German out of four is", "tokens": [6416, 11, 15727, 4167, 287, 2031, 460, 1239, 307, 13933, 355, 890, 355, 530, 2679, 503, 286, 1440, 318], "temperature": 0.0, "avg_logprob": -0.38270172706017125, "compression_ratio": 1.4055944055944056, "no_speech_prob": 0.03617946431040764}, {"id": 2, "seek": 0, "start": 14.76, "end": 24.28, "text": " denied the elementary right of free men and that is to make a free choice in 18 years of", "tokens": [6699, 262, 19823, 826, 286, 1479, 1450, 290, 326, 318, 284, 787, 257, 1479, 3572, 287, 1248, 812, 286], "temperature": 0.0, "avg_logprob": -0.38270172706017125, "compression_ratio": 1.4055944055944056, "no_speech_prob": 0.03617946431040764}, {"id": 3, "seek": 2428, "start": 24.28, "end": 34.84, "text": " peace and good faith. This generation of Germans has earned the right to be free, including", "tokens": [4167, 290, 922, 4562, 13, 770, 5270, 286, 16064, 468, 7366, 262, 826, 284, 307, 1479, 11, 1390], "temperature": 0.0, "avg_logprob": -0.2585943268566597, "compression_ratio": 1.44, "no_speech_prob": 3.225951772378721e-08}, {"id": 4, "seek": 2428, "start": 34.84, "end": 43.64, "text": " the right to unite their families and their needs in lasting peace with good will to all", "tokens": [262, 826, 284, 24558, 511, 4172, 290, 511, 2476, 287, 15727, 4167, 351, 922, 481, 284, 477], "temperature": 0.0, "avg_logprob": -0.2585943268566597, "compression_ratio": 1.44, "no_speech_prob": 3.225951772378721e-08}, {"id": 5, "seek": 4364, "start": 43.64, "end": 59.8, "text": " people. You live in a defender dial in the freedom, but your life.", "tokens": [50363, 661, 13, 921, 2107, 287, 257, 13191, 5980, 287, 262, 4925, 11, 475, 534, 1204, 13, 51171], "temperature": 0.0, "avg_logprob": -0.4429050746716951, "compression_ratio": 0.9705882352941176, "no_speech_prob": 8.880950190359727e-06}], "language": "en"}'


def generate_srt(transcript:  Iterator[dict]) -> str:
    tmp_file = NamedTemporaryFile(mode="w")
    with open(tmp_file.name, mode="w") as f:
        write_srt(transcript, f)
    with open(tmp_file.name, mode="r") as f:
        srt_txt = f.read()
    return srt_txt


def generate_vtt(transcript:  Iterator[dict]) -> str:
    tmp_file = NamedTemporaryFile(mode="w")
    with open(tmp_file.name, mode="w") as f:
        write_vtt(transcript, f)
    with open(tmp_file.name, mode="r") as f:
        srt_txt = f.read()
    return srt_txt


if __name__ == '__main__':
    import json

    result = json.loads(TEST_STR)
    print(generate_srt(result["segments"]))
    print('-------------------------------------------------')
    print(generate_vtt(result["segments"]))
