
import cv2
import numpy as np

# Parameters for lucas kanade optical flow
feature_params = dict(maxCorners=100, qualityLevel=0.3, minDistance=7, blockSize=7)
lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# function to calculate motion vectors using Lucas-Kanade optical flow
def calculate_motion_vectors(frame1, frame2, p0):
    # calculate optical flow
    flow = cv2.calcOpticalFlowPyrLK(frame1, frame2, p0, None, **lk_params)

    #flow = cv2.CalcOpticalFlowHS(frame1, frame2, None)
    return flow


# Function to compute distances between motion vectors in a frame
def compute_distances(motion_vectors):
    distances = []
    for i in range(len(motion_vectors) - 1):
        distance = cv2.norm(motion_vectors[i + 1] - motion_vectors[i])
        distances.append(distance)
    return distances


# Function to segment a shot into subshots using motion vector distances
def segment_shot_into_subshots(video_path, shots, threshold):
    cap = cv2.VideoCapture(video_path)
    subshots = []

    ret, old_frame = cap.read()
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

    tmp = 0
    end = 0

    for i in range(len(shots) - 1):
        tmpshots = shots
        _, frame1 = cap.read()
        _, frame2 = cap.read()
        # Take first frame and find corners in it
        old_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        new_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        motion_vectors = calculate_motion_vectors(old_gray, new_gray, p0)
        distances = compute_distances(motion_vectors)
        
        if min(distances) > threshold and i+1-end>30:
            subshot = tmpshots[tmp:i + 1]
            subshots.append(subshot)
            tmp = i + 1
            end = tmp

    subshots.append(shots[tmp:])
    return subshots


# Function to get the motion vector distances
def distanceListSet(video_path, shot):
    cap = cv2.VideoCapture(video_path)

    ret, old_frame = cap.read()
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)

    distanceList = []
    for i in range(len(shot) - 1):
        _, frame1 = cap.read()
        _, frame2 = cap.read()
        # Take first frame and find corners in it
        old_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        new_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        motion_vectors = calculate_motion_vectors(old_gray, new_gray, p0)
        distances = compute_distances(motion_vectors)
        distanceList.append(min(distances))

    return distanceList


# Function to segment subshots
def segment_subshots(video_path, shots):
    subshots = []
    newShots = []
    distanceList = []
    maxshots = []
    for i in range(len(shots)):
        if shots[i][1] - shots[i][0] < 30:
            continue
        newShots.append(range(shots[i][0], shots[i][1], 1))
        if shots[i][1] - shots[i][0] > len(maxshots):
            maxshots = newShots[-1]
        distanceList = distanceListSet(video_path, newShots)

    threshold = np.quantile(distanceList, 0.95)

    while len(subshots) == 0 or len(subshots) > 3:
        subshots = []
        range_to_point = segment_shot_into_subshots(video_path, maxshots, threshold)

        for j in range(len(range_to_point)):
            newSubshots = (range_to_point[j][0], range_to_point[j][-1])
            subshots.append(newSubshots)

        if len(subshots) > 3:
            threshold += 10
            # threshold *= 1.1

    # print(threshold)

    subshots = []
    for i in range(len(newShots)):
        
        range_to_point = segment_shot_into_subshots(video_path, newShots[i], threshold)
        
        subshotsList = []
        for j in range(len(range_to_point)):
            newSubshots = (range_to_point[j][0], range_to_point[j][-1])

            # segment_start_time_min = int(range_to_point[j][0] / (30 * 60))
            # segment_start_time_sec = int((range_to_point[j][0] / 30) % 60)
            # segment_end_time_min = int(range_to_point[j][-1] / (30*60))
            # segment_end_time_sec = int((range_to_point[j][-1] / 30) % 60)
            # print('Segment from %02d:%02d to %02d:%02d' % (segment_start_time_min, segment_start_time_sec, segment_end_time_min, segment_end_time_sec))

            subshotsList.append(newSubshots)
        # print('----------------------------shot-----------------------------')
        # if(len(subshotsList)>1):
        #    if subshotsList[-1][-1] - subshotsList[-1][0] < 30:
        #         subshotsList[-2] = (subshotsList[-2][0], subshotsList[-1][-1])
        #         subshotsList.pop()

        # print(subshotsList)

        subshots.append(subshotsList)
    # print(subshots)

    return subshots


# Get all subshots
def extract_subshots(video_path, shots):
    subshots = segment_subshots(video_path, shots)

    # print("==========subshots==========")
    print("Subshots segmentation complete")
    # print(subshots)

    return subshots