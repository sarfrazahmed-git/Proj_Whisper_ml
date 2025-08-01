import os
from io import BytesIO

def copy_dir_content(src,dest):
    dir_list = os.listdir(src)
    input_items = [os.path.join(src, item) for item in dir_list]
    output_items = [os.path.join(dest, item) for item in dir_list]

    for index in range(len(input_items)):
        with open(input_items[index], 'rb') as fsrc:
            with open(output_items[index], 'wb') as fdst:
                fdst.write(fsrc.read())

import torch
import numpy as np
import io
import scipy.io.wavfile
def tensor_to_wav_bytes(tensor: torch.Tensor, sample_rate: int) -> io.BytesIO:
    waveform = tensor.squeeze().cpu().numpy()

    waveform = np.clip(waveform, -1.0, 1.0)
    int16_waveform = (waveform * 32767).astype(np.int16)
    wav_io = io.BytesIO()
    scipy.io.wavfile.write(wav_io, sample_rate, int16_waveform)
    wav_io.seek(0)

    return wav_io


import ffmpeg

def convert_webm_bytes_to_wav(audio_bytes: bytes) -> BytesIO:
    input_io = BytesIO(audio_bytes)
    output_io = BytesIO()

    process = (
        ffmpeg
        .input('pipe:0', format='webm')
        .output('pipe:1', format='wav', ac=1, ar='16000')  # Mono, 16kHz
        .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
    )
    out, err = process.communicate(input=input_io.read())

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{err.decode()}")

    output_io.write(out)
    output_io.seek(0)
    return output_io
