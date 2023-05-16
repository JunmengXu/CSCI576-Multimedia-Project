import os
import numpy as np

# Define the width, height, fps and number of frames of the video
# Define sample rate of audio
WIDTH = 480
HEIGHT = 270
FPS = 30
CHS_PER_PIXEL = 3
AUDIO_SAMPLE_RATE = 44100


# Get total frames number of the input video
def get_frames_size(video_path):
    # Open the file and get its size
    with open(video_path, 'rb') as f:
        file_size = os.path.getsize(video_path)

    # Calculate the size of each frame
    frame_size = WIDTH * HEIGHT * CHS_PER_PIXEL

    # Calculate the number of frames
    num_frames = file_size // frame_size

    # print(f'The file contains {num_frames} frames.')
    return num_frames


# Get all frames of the input video
def get_frames(video_path, frame_size):
    # Set up the video capture object
    num_frames = frame_size

    frames = []
    with open(video_path, 'rb') as f:
        # Loop over the remaining frames
        for i in range(0, num_frames):
            # Read the current frame
            data = f.read(WIDTH * HEIGHT * CHS_PER_PIXEL)
            curr_frame = np.frombuffer(data, dtype=np.uint8).reshape((HEIGHT, WIDTH, CHS_PER_PIXEL))

            frames.append(curr_frame)
    
    return frames
    