# Extracting indexes from video along with interactive exploration


## Object
A solution to
1. Arrive at this logical index or table of contents in an automated manner given a video with audio as input.
2. Once the index or table of contents is extracted, you want to show it in an interactive player setup where you can jump to any index to browse the video/audio and change it interactively allowing interactive exploration.


## Run
Put InputVideo.mp4, InputVideo.rgb, and InputAudio.wav in folder "data"

The width, height, fps of the video should be:
	WIDTH = 480
	HEIGHT = 270
	FPS = 30

Sample rate of audio should be:
	AUDIO_SAMPLE_RATE = 44100

Then run

	- python main.py InputVideo.mp4 InputVideo.rgb InputAudio.wav


## Interface
![Alt text](/interface.png?raw=true "Title")
