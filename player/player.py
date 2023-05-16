import tkinter as tk
import cv2
from PIL import Image, ImageTk
from pydub import AudioSegment
import pydub.playback as playback
from tkinter import ttk
import threading
import pygame


# Define classes for scene, shot, subshot
class Subshot:
    def __init__(self, startsub, endsub):
        self.stat = startsub
        self.end = endsub

class Shot:
    def __init__(self, startShot, endShot,subshotslist):
        self.startframe = startShot
        self.endframe = endShot
        self.subshots = []
        for i in subshotslist:
            self.subshots.append(Subshot(i[0], i[1]))

class Sence:
    def __init__(self, startScene, endScene, shotslist):
        self.startscene = startScene
        self.endscene = endScene
        self.shots = []
        for i in shotslist:
            self.shots.append(Shot(i[0], i[1], i[2]))


font1 = ['Times', 14, 'normal']
font2 = ["Times", 18, "bold italic"]
movieName = "Movie"

class App:
    def __init__(self, window, window_title, videosegments, audio_file, num_frames, raw_frames):

        self.window = window
        self.window.title(window_title)
        self.videosegments = []
        self.playFlag = True
        self.stopFlag = False

        # Define the width, height of frames of the video
        self.width = 480
        self.height = 270
        self.fps = 30

        # Shared frame number, which is playing
        self.frame_number = tk.IntVar()
        self.frame_number.set(0)
        
        # Index of last frame played
        self.last_frame = tk.IntVar()
        self.last_frame.set(0)


        self.audio_stop_flag = False
        self.indexframe = tk.Frame(self.window)


        for i in videosegments:
            # print(i[0], i[1], i[2])
            self.videosegments.append(Sence(i[0], i[1], i[2]))


        style = ttk.Style(self.window)
        style.theme_use("default")  # set theam to clam
        style.configure("Treeview", background="white",
                        fieldbackground="white", foreground="black", font=font1)
        style.configure('Treeview.Heading', background="PowderBlue", font=font2)

        self.trv = ttk.Treeview(self.indexframe, selectmode='browse', height=14)
        self.trv.grid(row=0, column=0, rowspan=10, padx=5)
        self.indexframe.grid(row=1, column=0, padx=10)
        # number of columns
        self.trv["columns"] = ("1")
        # Defining heading
        self.trv['show'] = 'tree headings'
        # trv['show'] = 'tree'

        # width of columns and alignment
        self.trv.column("#0", width=200, anchor='w')
        self.trv.column("1", width=130, anchor='w')

        # Headings
        # respective columns
        self.trv.heading("#0", text=movieName)
        self.trv.heading("1", text="Duration")
        for sence in range(len(self.videosegments)):
            self.trv.insert("", 'end', iid=str(self.videosegments[sence].startscene), open=True, text='Scene' + str(sence+1), tags=str(self.videosegments[sence].startscene),
                       values=[str( round((self.videosegments[sence].endscene - self.videosegments[sence].startscene) / self.fps, 1) ) + 's'])
            for shots in range(len(self.videosegments[sence].shots)):
                self.trv.insert(str(self.videosegments[sence].startscene), 'end', iid='*'+str(self.videosegments[sence].shots[shots].startframe), open=True,
                           text='Shots' + str(shots + 1), tags='#'+str(self.videosegments[sence].shots[shots].startframe),
                           values=[str( round((self.videosegments[sence].shots[shots].endframe-self.videosegments[sence].shots[shots].startframe) / self.fps, 1) ) + 's' ])
                for subshots in range(len(self.videosegments[sence].shots[shots].subshots)):
                    self.trv.insert('*'+str(self.videosegments[sence].shots[shots].startframe), 'end', iid='**'
                                      + str(self.videosegments[sence].shots[shots].subshots[subshots].stat),
                                    open=True,
                                    text='Subshots' + str(subshots + 1), tags='##'+str(self.videosegments[sence].shots[shots].subshots[subshots].stat),
                                    values=[str( round((self.videosegments[sence].shots[shots].subshots[subshots].end - self.videosegments[sence].shots[shots].subshots[subshots].stat) / self.fps, 1) ) + 's' ])
        self.trv.bind("<<TreeviewSelect>>", self.keyframe_start)  # on select event


        # Load the frames from the video and convert them to grayscale
        self.frames = []
        # Set up the video capture object
        num_frames = num_frames
        
        for i in range(0, num_frames):
            # Read the current frame
            curr_frame = cv2.cvtColor(raw_frames[i], cv2.COLOR_RGB2BGR)
            self.frames.append(curr_frame)


        self.total_frames = num_frames
        self.delay = 27
      

        self.audio = AudioSegment.from_file(audio_file)
        self.duration_seconds = self.total_frames / self.fps * 1000
        # print(self.duration_seconds)
        self.audio = AudioSegment.from_file(audio_file, start_second=0, duration=self.duration_seconds)
        self.audio_stream = None
        self.paused = False
        self.exit_flag = False
        # print(self.delay)

        
        self.playerframe = tk.Frame(self.window)
        self.playerframe.grid(row=1, column=1, pady=5)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(self.playerframe, width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0)


        self.audio_path = audio_file
        #self.audio_thread = threading.Thread(target=self.play_sound, args=())
        self.playing = False
        self.audio_start = 0
        self.selections = []


        # Components
        self.buttonframe = tk.Frame(self.playerframe)
        self.buttonframe.columnconfigure(0, weight=1)
        self.buttonframe.columnconfigure(1, weight=1)
        self.buttonframe.columnconfigure(2, weight=1)
        self.btn_play = tk.Button(self.buttonframe, text="Play", width=6, command=self.play)
        self.btn_play.grid(row=0, column=0, padx=10)
        self.btn_pause = tk.Button(self.buttonframe, text="Pause", width=6,  command=self.pause)
        self.btn_pause.grid(row=0, column=1, padx=10)
        self.btn_stop = tk.Button(self.buttonframe, text="Stop", width=6, command=self.stop)
        self.btn_stop.grid(row=0, column=2, padx=10)
        self.buttonframe.grid(row=1, column=0, pady=10)

        self.progress = ttk.Progressbar(self.playerframe, orient=tk.HORIZONTAL, length=self.width-50, mode='determinate')
        self.progress.grid(row=2, column=0)
        self.scale = tk.Scale(self.playerframe, from_=0, to=self.total_frames - 1, orient=tk.HORIZONTAL, length=self.width - 50,
                              showvalue=0,
                              command=lambda x: self.set_frame(int(x)))
        self.scale.grid(row=3, column=0)


        # Initial audio
        pygame.init()
        pygame.mixer.init()
        self.audio_file = audio_file
        pygame.mixer.music.load(self.audio_file)
        pygame.mixer.music.play(-1, 0.0)


        # Start the highlighted segment selection task in a separate thread
        t = threading.Thread(target=self.checkHighlight)
        t.start()


        self.update()


        self.window.mainloop()


    # Continuously the highlighted segment selection
    def checkHighlight(self):
        self.set_white()
        tmpScene = 0
        tmpShots = 0
        tmpsubs = 0
        self.selections = []  # list of ids of matching tree entries
        for i in range(len(self.videosegments)):
            if self.frame_number.get() <= self.videosegments[i].endscene:
                self.trv.tag_configure(str(self.videosegments[i].startscene), background='orange')
                self.selections.append(str(self.videosegments[i].startscene))
                tmpScene = i
                break
        for i in range(len(self.videosegments[tmpScene].shots)):
            if self.frame_number.get() <= self.videosegments[tmpScene].shots[i].endframe:
                self.trv.tag_configure('#'+ str(self.videosegments[tmpScene].shots[i].startframe), background='orange')
                self.selections.append('#'+ str(self.videosegments[tmpScene].shots[i].startframe))
                tmpShots = i
                break
        for i in range(len(self.videosegments[tmpScene].shots[tmpShots].subshots)):
            if self.frame_number.get() <= self.videosegments[tmpScene].shots[tmpShots].subshots[i].end:
                self.trv.tag_configure('##' + str(self.videosegments[tmpScene].shots[tmpShots].subshots[i].stat), background='orange')
                self.selections.append('##'+ str(self.videosegments[tmpScene].shots[tmpShots].subshots[i].stat))
                break

        self.window.after(1, self.checkHighlight)


    # Jump frame function for selection in scrollbar
    def keyframe_start(self, event):
        frame_id = self.trv.selection()[0]  # collect selected row id
        if len(frame_id)>1:
            for i in range(len(frame_id)):
                if frame_id[i]!= '*':
                    self.frame_number.set(int(frame_id[i:]))
                    break
        else:
            self.frame_number.set(int(frame_id))

        self.set_white()
        self.trv.tag_configure(frame_id, background="orange")

        self.last_frame.set(self.frame_number.get())
       
        pygame.mixer.music.play(-1, self.frame_number.get() / 30)
        

    # For drag button
    def set_frame(self, frame):
        self.frame_number.set(frame)
        self.last_frame.set(frame)
        self.set_white()
       
        pygame.mixer.music.play(-1, frame / (30))


    def exit(self):
        playback.play(None)
        self.window.quit()

    def pause(self):
        self.playFlag = False

    def play(self):
        self.playFlag = True
        self.stopFlag = False

    def stop(self):
        self.stopFlag = True
        self.playFlag = False
        self.audio_stop_flag = True


    # Set segment selection with white background color
    def set_white(self):
        for i in range(len(self.selections)):
            self.trv.tag_configure(self.selections[i], background="white")
    

    # update continuously
    def update(self):
        # if playing currently
        if self.playFlag:
            
            frame = self.frames[self.frame_number.get()]

            if self.audio_stop_flag:
                pygame.mixer.music.play(-1, 0.0)
                self.audio_stop_flag = False
            else:
                pygame.mixer.music.unpause()
            
            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.image = Image.fromarray(self.frame)
            self.photo = ImageTk.PhotoImage(image=self.image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            
            self.progress['value'] = self.frame_number.get() / self.total_frames * 100
            
            audio_pos = pygame.mixer.music.get_pos()
            expect_frame = round(audio_pos / 1000 * 30) + self.last_frame.get()
            # if abs(expect_frame - self.frame_number.get()) > 3:
            self.frame_number.set(expect_frame)

            self.frame_number.set((self.frame_number.get()+1) % self.total_frames)
            
            self.window.after(self.delay, self.update)
           

        # if stop the play
        elif self.stopFlag:
            self.frame_number.set(0)
            self.set_white()
            self.last_frame.set(0)
            self.window.after(0, self.update)
            self.scale.set(0)
            pygame.mixer.music.stop()


        # if pause the play
        else:
            self.progress['value'] = self.frame_number.get() / self.total_frames * 100
            self.last_frame.set(self.frame_number.get())
            self.window.after(0, self.update)
            self.scale.set(self.frame_number.get())
            pygame.mixer.music.set_pos(self.frame_number.get() / 30)
            pygame.mixer.music.pause()



# Create a window and pass it to the Application object
def run_player(audio_path, video_segments, num_frames, frames):

    # Data only for Test
    # KFramesList = [[0, 200,[[0,45,[[0,35],[36,45]]], [46,160,[[46,100],[101,120],[121,160]]],[161,200,[[161,180],[181,200]]]]], [201, 5000,[[201,2000,[[201,1000],[1001,2000]]], [2001,4000,[[2001,2500],[2501,3000],[3001,4000]]],[4001,5000,[[4001,4500],[4501,5000]]]]]]
    
    App(tk.Tk(), "Spring 2023 CSCI 576 Multimedia Project", video_segments, audio_path, num_frames, frames)

# run_player("../data/InputVideo.rgb", "../data/InputAudio.wav", [])