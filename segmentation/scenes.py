import cv2
import os
import numpy as np

# Define the width, height, fps and number of frames of the video
WIDTH = 480
HEIGHT = 270
FPS = 30
BYTES_PER_PIXEL = 3
AUDIO_SAMPLE_RATE = 44100


# Find the optimal cutpoint of a list of number
def find_optimal_cutpoint(difs):
    difs_sorted = sorted(difs)
    n = len(difs)
    sum_left = [0] * n
    sum_right = [0] * n

    # Compute sums of left and right segments for each cutpoint
    for i in range(1, n):
        sum_left[i] = sum_left[i-1] + difs_sorted[i-1]
        sum_right[n-i-1] = sum_right[n-i] + difs_sorted[n-i]

    # Find cutpoint that minimizes absolute difference
    abs_diff = [abs(sum_left[i] - sum_right[i]) for i in range(1, n)]
    min_index = abs_diff.index(min(abs_diff))

    # Return optimal cutpoint
    return difs_sorted[min_index]


# Calculate the mean average distance in pixel values between two frames
def mean_pixel_distance(left, right):

    num_pixels = float(left.shape[0] * left.shape[1])

    return (np.sum(np.abs(left.astype(np.int32) - right.astype(np.int32))) / num_pixels)


WEIGHTS = {
    'delta_hue': 1.0,
    'delta_sat': 1.0,
    'delta_lum': 1.0,
}


# Calculate the score for each adjacent frames
def calculate_frame_score(last_frame, frame_img):
    # Convert image into HSV colorspace.
    last_hue, last_sat, last_lum = cv2.split(cv2.cvtColor(last_frame, cv2.COLOR_RGB2HSV))
    hue, sat, lum = cv2.split(cv2.cvtColor(frame_img, cv2.COLOR_RGB2HSV))

    score_components = {
        'delta_hue': mean_pixel_distance(hue, last_hue),
        'delta_sat': mean_pixel_distance(sat, last_sat),
        'delta_lum': mean_pixel_distance(lum, last_lum),
    }

    frame_score = (sum(score_components[key] * WEIGHTS[key] for key in score_components)
                   / sum(abs(WEIGHTS[key]) for key in WEIGHTS))

    return frame_score


# Check whether it is a new scene
def process_frame(frame_img, last_frame, threshold):
        
    frame_score = calculate_frame_score(last_frame, frame_img)

    # Any frame over the threshold a new scene
    if frame_score >= threshold:
        return True
    
    return False
        

# Get frame score for adjacent frames
def get_frame_score(frame_img1, frame_img2):
    frame_score = calculate_frame_score(frame_img1, frame_img2)
    return frame_score


# scene


def segment_scenes(shots, frames):
    # Compute the color feature of each shot
    frames_scores = []

    for i in range(len(frames)-2):
        frame_score = get_frame_score(frames[i], frames[i+1])
        frames_scores.append(frame_score)


    scenes = []
    scene_start_time = 0


    threshold = np.quantile(frames_scores, 0.996)

    if threshold < 35:
        threshold = 35
    else:
        threshold = (threshold+35)/2


    for i in range(0, len(shots)-1):
        
        divide = False
        for j in range(-25, 26):
            cur_frame = frames [ shots[i][1]+j ]
            next_frame = frames [ shots[i][1]+j+1 ]

            divide = process_frame(cur_frame, next_frame, threshold)

            if divide:
                break

        if divide :
            scenes.append((shots[scene_start_time][0], shots[i][1]))

            # segment_start_time_min = int(shots[scene_start_time][0] / (30*60))
            # segment_start_time_sec = int((shots[scene_start_time][0] / 30) % 60)
            # segment_end_time_min = int(shots[i][1] / (30*60))
            # segment_end_time_sec = int((shots[i][1] / 30) % 60)
            # print('Scene from %02d:%02d to %02d:%02d' % (segment_start_time_min, segment_start_time_sec, segment_end_time_min, segment_end_time_sec))

            scene_start_time = i+1


    scenes.append((shots[scene_start_time][0], shots[len(shots)-1][1]))

    # segment_start_time_min = int(shots[scene_start_time][0] / (30*60))
    # segment_start_time_sec = int((shots[scene_start_time][0] / 30) % 60)
    # segment_end_time_min = int(shots[len(shots)-1][1] / (30*60))
    # segment_end_time_sec = int((shots[len(shots)-1][1] / 30) % 60)
    # print('Scene from %02d:%02d to %02d:%02d' % (segment_start_time_min, segment_start_time_sec, segment_end_time_min, segment_end_time_sec))

    return scenes


# Get scenes by this function
def extract_scenes(shots, frames):

    scenes = segment_scenes(shots, frames)

    # print("==========scenes==========")
    print("Scenes segmentation complete")
    # print(scenes)

    return scenes