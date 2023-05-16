import segmentation.shots as shots
import segmentation.scenes as scenes
import segmentation.subshots as subshots
import segmentation.utils as utils
import player.player as player
import sys

# # Specify the input video file path
# input_video_mp4 = "data/InputVideo.mp4"
# input_video_rgb = "data/InputVideo.rgb"
# input_audio_wav = "data/InputAudio.wav"

input_video_mp4 = 'data/' + sys.argv[1]
input_video_rgb = 'data/' + sys.argv[2]
input_audio_wav = 'data/' + sys.argv[3]


# Get total frames number of the input video
frames_number = utils.get_frames_size(input_video_rgb)
print("This video has %d frames" %(frames_number))

# Get all original frames
frames = utils.get_frames(input_video_rgb, frames_number)

# Call the function to segment the video into shots
shots_list = shots.extract_shots(input_video_rgb, frames_number, frames)

# Call the function to group the shots into scenes
scene_list = scenes.extract_scenes(shots_list, frames)

# Call the function to segment the shots into subshots
subshot_list = subshots.extract_subshots(input_video_mp4, shots_list)


# Match scenes, shots and subshot together as a single list
scene_shots_subshots = []
for scene in scene_list:

    new_scene = []
    start_frame, end_frame = scene
    new_scene.append(start_frame)
    new_scene.append(end_frame)

    new_shots = []
    
    for i, shot in enumerate(shots_list):
        shot_start, shot_end = shot
        if start_frame <= shot_start and shot_end <= end_frame:

            cur_shot = []
            cur_shot.append(shot_start)
            cur_shot.append(shot_end)
            if len(subshot_list[i]) > 1:
                cur_shot.append(subshot_list[i])
            else:
                cur_shot.append([])
            new_shots.append(cur_shot)


    new_scene.append(new_shots)

    scene_shots_subshots.append(new_scene)
            
print("==============Scene_Shots_Subshots==============")
print(scene_shots_subshots)
print("================================================")


print("Ready to play")
# Call the function to play the segmented video and audio files
player.run_player(input_audio_wav, scene_shots_subshots, frames_number, frames)
