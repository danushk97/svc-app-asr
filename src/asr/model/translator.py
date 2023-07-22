import whisper


model = whisper.load_model('large')


def translate(file_path: str):
    return model.transcribe(file_path, task="translate")
