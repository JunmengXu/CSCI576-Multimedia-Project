import cv2
import os
import numpy as np

# Define the width, height, fps and number of frames of the video
# Define sample rate of audio
WIDTH = 480
HEIGHT = 270
FPS = 30
CHS_PER_PIXEL = 3
AUDIO_SAMPLE_RATE = 44100


# Define a function to compute the color histogram of an image
def compute_color_histogram(image):
    # Define the number of bins for each channel
    hist_size = [64, 64, 64]

    # Define the range for each channel
    ranges = [0, 256, 0, 256, 0, 256]

    # Define the color channels to include in the histogram
    channels = [0, 1, 2]

    histogram = cv2.calcHist([image], channels, None, hist_size, ranges)
    histogram = cv2.normalize(histogram, histogram).flatten()

    return histogram


# Normalize a list of data to [0,1]
def normalize(data):
    # Convert the list to a numpy array
    arr = np.array(data)

    # Normalize the array between 0 and 1
    norm_arr = (arr - np.min(arr)) / (np.max(arr) - np.min(arr))

    return norm_arr


# Find the optimal cutpoint of a list of data
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


# Extract difference of each adjacent frames
def extract_difs(video_path, frames_number):

    # Set up the video capture object
    num_frames = frames_number
    difs = []

    with open(video_path, 'rb') as f:
        data = f.read(WIDTH * HEIGHT * 3)
        prev_frame = np.frombuffer(data, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_RGB2GRAY)

        # Loop over the remaining frames
        for i in range(1, num_frames):
            # Read the current frame
            data = f.read(WIDTH * HEIGHT * 3)
            curr_frame = np.frombuffer(data, dtype=np.uint8).reshape((HEIGHT, WIDTH, 3))

            # Convert BGR to grayscale
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_RGB2GRAY)

            # Calculate the absolute difference between the current and previous frames
            diff = cv2.absdiff(curr_gray, prev_gray)

            # Update the sum and count of absolute differences
            difs.append(diff.sum())

            # Update the previous frame
            prev_gray = curr_gray
    
    return difs


# Segement shots
def segment_shots(video_path, threshold, difs, frames_number, frames):
    # Set up the video capture object
    num_frames = frames_number

    # Initialize the start time of the current segment
    segment_start_time = 0

    segment_index = 0;

    segments = []
    
    # Compute the color histogram of each shot
    histograms_color_frames = [compute_color_histogram(frame) for frame in frames]

    similarities_color = []

    for i in range(len(frames)-2):
        histogram_color_1 = histograms_color_frames[i]

        histogram_color_2 = histograms_color_frames[i+1]

        similarity_color = cv2.compareHist(histogram_color_1, histogram_color_2, cv2.HISTCMP_INTERSECT)
    
        similarities_color.append(similarity_color)

    similarities_color = normalize(similarities_color)

    threshold_color = np.quantile(similarities_color, 0.2)
    # print(similarities_color)
    # print(threshold_color)

    # Loop over the remaining frames
    for i in range(1, num_frames):
        
        # Calculate the absolute difference between the current and previous frames
        diff = difs[i-1]

        segment_end_time = i-1

        maxDiff = diff

        # If the difference is above the threshold, save the previous segment
        if diff > threshold and segment_start_time / FPS - segment_end_time / FPS <= -1 and similarities_color[i-1]<threshold_color:

            new_segment_end_time = segment_end_time
            for j in range(1, 25):
                if i - 1 + j >= len(difs):
                    break
                if difs[i-1+j] > maxDiff and similarities_color[i-1+j]<threshold_color:
                    maxDiff = difs[i-1+j]
                    new_segment_end_time = i-1+j
            
            segment_end_time = new_segment_end_time 

            segments.append((segment_start_time, segment_end_time))

            # segment_start_time_min = int(segment_start_time / (30*60))
            # segment_start_time_sec = int((segment_start_time / 30) % 60)
            # segment_end_time_min = int(segment_end_time / (30*60))
            # segment_end_time_sec = int((segment_end_time / 30) % 60)
            # print('Shots from %02d:%02d to %02d:%02d' % (segment_start_time_min, segment_start_time_sec, segment_end_time_min, segment_end_time_sec))

            # Start a new segment
            segment_start_time = segment_end_time + 1

            segment_index = segment_index + 1



    # Release the video capture object
    segments.append((segment_start_time, num_frames-1))

    # segment_start_time_min = int(segment_start_time / (30*60))
    # segment_start_time_sec = int((segment_start_time / 30) % 60)
    # segment_end_time_min = int(num_frames / (30*60))
    # segment_end_time_sec = int((num_frames / 30) % 60)
    # print('Segment from %02d:%02d to %02d:%02d' % (segment_start_time_min, segment_start_time_sec, segment_end_time_min, segment_end_time_sec))

    # print("There are %d shots" %(segment_index+1) )

    return segments


# Get shots by this function
def extract_shots(video_rgb_path, frames_number, frames):

    difs = extract_difs(video_rgb_path, frames_number)

    diff_thre1 = find_optimal_cutpoint(difs)
    diff_thre2 = np.quantile(difs, 0.9)

    shots = segment_shots(video_rgb_path, (diff_thre1+diff_thre2), difs, frames_number, frames)

    # print("==========shots==========")
    print("Shots segmentation complete")
    # print(shots)

    return shots

