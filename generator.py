import whisper
import os
import torch
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


class LyricsGenerator:
    def __init__(self):
        self.model = whisper.load_model("medium")

    def generate(self, audio):
        audio = whisper.load_audio(audio)
        audio = whisper.pad_or_trim(audio)

        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        _, probs = self.model.detect_language(mel)

        options = whisper.DecodingOptions(fp16=False)
        result = whisper.decode(self.model, mel, options=options)
        return result.text


# if __name__ == "__main__":
#     generator = LyricsGenerator()
#     res = generator.generate("file_0.mp3")
#     print(res)
