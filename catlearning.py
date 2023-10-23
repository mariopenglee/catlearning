from cProfile import label
from cgitb import text
from ctypes import resize
import re
import tkinter as tk
from tkinter import ttk
import os
import random
from tkinter import font
from turtle import bgcolor, width
from urllib import response
from venv import create

from ipykernel import connect_qtconsole
import cv2
import pygame
from PIL import Image, ImageTk

import time

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ExperimentApp:
    def __init__(self, root):
        
        ###
        # replay video when showing correct answer,  DONE
        # dont let them click next until video finishes DONE
        # add timer DONE
        # add panels in between parts.

        self.shuffle = False
        self.has_replay = False
        self.has_timer = False
        self.broad_to_narrow = True


        
        self.root = root
        self.root.title("Experiment")
        self.window_width = 600
        self.window_height = 500
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        # add padding to the root window
        self.bg_color = "white"
        self.root.config(padx=20, pady=20, bg=self.bg_color)

        self.last_img = None  # Store PhotoImage object for the last frame of the video
        self.training_folder = resource_path("videos/training")
        self.broad_folder = resource_path("videos/broad")
        self.narrow_folder = resource_path("videos/narrow")
        self.broad_test_folder = resource_path("videos/broad_test")
        self.narrow_test_folder = resource_path("videos/narrow_test")

        self.part1_panel = resource_path("panels/part1.gif")   
        self.part2_panel = resource_path("panels/part2.gif")
        self.part3_panel = resource_path("panels/part3.gif")
        self.instructions_panel = resource_path("panels/instructions.png")
        self.end_panel = resource_path("panels/end.png")

        self.training_images = [f for f in os.listdir(self.training_folder) if f.endswith(".jpg")]
        self.broad_videos = [f for f in os.listdir(self.broad_folder) if f.endswith(".mp4")]
        self.narrow_videos = [f for f in os.listdir(self.narrow_folder) if f.endswith(".mp4")]
        self.broad_test_videos = [f for f in os.listdir(self.broad_test_folder) if f.endswith(".mp4")]
        self.narrow_test_videos = [f for f in os.listdir(self.narrow_test_folder) if f.endswith(".mp4")]

        if self.shuffle:
            random.shuffle(self.broad_videos)
            random.shuffle(self.narrow_videos)
            random.shuffle(self.broad_test_videos)
            random.shuffle(self.narrow_test_videos)
        else:
            # sort the videos by number in the filename
            self.broad_videos.sort(key=lambda f: int(f.split(".")[0]))
            self.narrow_videos.sort(key=lambda f: int(f.split(".")[0]))
            self.broad_test_videos.sort(key=lambda f: int(f.split(".")[0]))
            self.narrow_test_videos.sort(key=lambda f: int(f.split(".")[0]))

        self.video_width = 400
        self.video_height = 250

        self.current_trial_index = 0

        # Audio handling
        self.audio_folder = resource_path("audios")
        self.audio_files = [f for f in os.listdir(self.audio_folder) if f.endswith(".mp3")]

        self.broad_options = ["Lat", "Rall", "None"]
        self.narrow_options = ["Wug", "Dax", "None"]

        self.broad_audio = ["lat.mp3", "rall.mp3", "none.mp3"]
        self.narrow_audio = ["wug.mp3", "dax.mp3", "none.mp3"]

        self.training_audio = ["cup.mp3", "hat.mp3", "none.mp3"]

        self.training_key = [
            "Cup",
            "Hat",
            "None",
        ]
        self.broad_key = [
            "Rall",
            "Rall",
            "Lat",
            "Lat",
            "None",
            "Rall",
            "Lat",
            "Lat",
            "Rall",
            "None",
            "Lat",
            "Lat",
            "Rall",
            "Rall",
            "None",
            "Lat",
            "Rall",
            "Rall",
            "Lat",
            "None",
        ] 

        self.narrow_key = [
            "Dax",
            "Wug",
            "Wug",
            "Dax",
            "None",
            "Wug",
            "Wug",
            "Dax",
            "Dax",
            "None",
            "Wug",
            "Dax",
            "Dax",
            "Wug",
            "None",
            "Dax",
            "Dax",
            "Wug",
            "Wug",
            "None",
        ]

        self.narrow_test_key = [
            "Dax",
            "Dax",
            "Wug",
            "Wug",
            "None",
            "Dax",
            "Wug",
            "Wug",
            "Dax",
            "None",
            "Wug",
            "Wug",
            "Dax",
            "Dax",
            "None",
            "Wug",
            "Dax",
            "Dax",
            "Wug",
            "None",
        ]

        self.broad_test_key = [
            "Rall",
            "Lat",
            "Lat",
            "Rall",
            "None",
            "Lat",
            "Lat",
            "Rall",
            "Rall",
            "None",
            "Lat",
            "Rall",
            "Rall",
            "Lat",
            "None",
            "Rall",
            "Rall",
            "Lat",
            "Lat",
            "None",
        ]

        self.video_files = []
        self.current_video_folder = "videos" 

        self.answer_key = []

        self.current_audio_files = []
        
        if self.broad_to_narrow:
            self.video_files = self.broad_videos + self.narrow_videos + self.narrow_test_videos
            self.answer_key = self.broad_key + self.narrow_key + self.narrow_test_key
        else:
            self.video_files = self.narrow_videos + self.broad_videos + self.broad_test_videos
            self.answer_key = self.narrow_key + self.broad_key + self.broad_test_key

        pygame.init()
        self.disable_options = False

        self.current_section = 0 # 0 is training, 1 is normal, 2 is variation, 3 is testing.

        

        
        self.create_widgets()  # Start with the broad options

    def create_widgets(self):
        self.video_label = ttk.Label(self.root)
        self.video_label.config(borderwidth=0, relief="raised")
        self.video_label.pack()
        self.create_next_button() 
        # make the buttons squares
        if self.has_replay:
            self.create_replay_button()

        self.start_training()

    def start_training(self):
        self.option_labels = ["Cup", "Hat", "None"]
        self.current_audio_files = self.training_audio
        self.current_section = 0
        self.disable_options = True
        self.create_option_buttons()
        self.show_panel(0)

    def load_next_image(self):
        if self.current_trial_index < len(self.training_images):
            image_filename = self.training_images[self.current_trial_index-1]
            self.current_trial_index += 1
            # load the image
            image_path = os.path.join(self.training_folder, image_filename)
            image = Image.open(image_path)
            image = image.resize((self.video_width, self.video_height))
            self.last_img = ImageTk.PhotoImage(image=image)
            self.video_label.config(image=self.last_img)
            self.root.update()
            self.show_buttons_with_audio()
        else:
            self.current_trial_index = 0
            # self.current_trial_index = 39

            self.show_panel(1)
            

    def show_panel(self, panel_number):
        self.destroy_option_buttons()
        if panel_number == 0:
            # instructions
            self.current_section = 0
            panel_path = self.instructions_panel
            self.option_labels = ["Cup", "Hat", "None"]
            

        if panel_number == 1:
            # first phase
            self.current_section = 1
            if self.broad_to_narrow:
                self.option_labels = ["Lat", "Rall", "None"]
                self.current_audio_files = self.broad_audio
                self.current_video_folder = self.broad_folder
            else:
                self.option_labels = ["Wug", "Dax", "None"]
                self.current_audio_files = self.narrow_audio
                self.current_video_folder = self.narrow_folder
            
            panel_path = self.part1_panel
        elif panel_number == 2:
            # switch phase
            self.current_section = 2
            panel_path = self.part2_panel
            if (self.broad_to_narrow):
                self.option_labels = ["Wug", "Dax", "None"]
                self.current_audio_files = self.narrow_audio
                self.current_video_folder = self.narrow_folder
            else:
                self.option_labels = ["Lat", "Rall", "None"]
                self.current_audio_files = self.broad_audio
                self.current_video_folder = self.broad_folder
        elif panel_number == 3:
            # testing phase
            self.current_section = 3
            panel_path = self.part3_panel
            if (self.broad_to_narrow):
                self.option_labels = ["Wug", "Dax", "None"]
                self.current_audio_files = self.narrow_audio
                self.current_video_folder = self.narrow_test_folder
            else:
                self.option_labels = ["Lat", "Rall", "None"]
                self.current_audio_files = self.broad_audio
                self.current_video_folder = self.broad_test_folder
        else:
            panel_path = self.instructions_panel
        gif = Image.open(panel_path)
        # let it occupy the whole screen and display a text saying "Part 1"
        gif = gif.resize((self.window_width, self.window_height))
        background = ImageTk.PhotoImage(image=gif)
        background_label = tk.Label(self.root, image=background)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        intro = tk.Label(self.root, text="Part " + str(panel_number), font=('Helvetica', '50'), bg=self.bg_color)
        intro.place(x=self.window_width / 2, y=self.window_height / 2, anchor="center")
        self.root.update()
        self.root.after(2000)
        intro.destroy()
        background_label.destroy()
        self.create_option_buttons()
        self.load_next_video()
    

    def create_option_buttons(self):
        self.option_buttons = []
        for i, option_label in enumerate(self.option_labels):
            button = tk.Button(self.root, text=option_label, command=lambda option_label=option_label: self.select_option(option_label), font=('Helvetica', '30'), width=7, height=3, bg=self.bg_color)
            button.config(borderwidth=0, highlightthickness=0, relief="raised")
            # display with absolute position
            distance_between_buttons = 200
            # horizontal padding is calculated based on screen width, button width and distance between buttons, there's gonna be 3 buttons, also 20 for padding.
            horizontal_padding = (self.window_width - 2 * 200 - 3 * 10) / 2
            # vertical offset is calculated based on the video height
            vertical_offset = self.video_height + 150

            button.place(x=horizontal_padding + i * distance_between_buttons, y=vertical_offset, anchor="center")
            self.option_buttons.append(button)

    def create_next_button(self):
        self.next_button = tk.Button(self.root, text="Next", command=self.load_next_video, font=('Helvetica', '15'), bg=self.bg_color)
        self.next_button.config(borderwidth=0, highlightthickness=0, relief="raised")
        self.next_button.place(x=self.window_width - 50, y=0, anchor="ne")

    def create_replay_button(self):
        self.replay_button = tk.Button(self.root, text="Replay", command=self.replay_video, font=('Helvetica', '15'), bg=self.bg_color)
        self.replay_button.config(borderwidth=0, highlightthickness=0, relief="raised")
        self.replay_button.pack()


    def destroy_option_buttons(self):
        for button in self.option_buttons:
            button.destroy()


    def play_audio(self, audio_filename):
        audio_path = os.path.join(self.audio_folder, audio_filename)
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

    def show_buttons_with_audio(self):
        self.disable_options = True
        if self.has_replay:
            self.replay_button.destroy()
        
        self.root.update()

        for audio_filename, button in zip(self.current_audio_files, self.option_buttons):
            
            self.play_audio(audio_filename)
            
            # scale the button to be bigger with animation, then scale back to normal
            for i in range(30, 60):
                button.config(font=('Helvetica', i))
                self.root.update()
            for i in range(60, 30, -1):
                button.config(font=('Helvetica', i))
                self.root.update()
            button.config(font=('Helvetica', 30), width=7, height=3)
            self.root.update()
            self.root.after(1000)  # Play each audio for 1 second

        self.disable_options = False


    def load_next_video(self):
        self.disable_options = True
        self.destroy_option_buttons()
        self.create_option_buttons()
        self.next_button.destroy()
        if self.has_replay:
            self.replay_button.destroy()
        if self.current_section == 0:
            self.load_next_image()
            return
        if self.current_trial_index < len(self.video_files):
            if self.current_trial_index == 20 and self.current_section != 2:
                self.show_panel(2)
                return
            if self.current_trial_index == 40 and self.current_section != 3:
                self.show_panel(3)
                return
            video_filename = self.video_files[self.current_trial_index]
            self.current_trial_index += 1
            self.play_video(video_filename)
            self.show_buttons_with_audio()
            if self.has_replay:
                self.create_replay_button()
            self.play_video(video_filename)

            ### timer
            if self.has_timer:
                self.start_time = time.time()
            
        else:
            self.end_experiment()




    def replay_video(self):
        # replay the current video
        video_filename = self.video_files[self.current_trial_index - 1]
        self.play_video(video_filename)        

    def play_video(self, filename):
        video_path = os.path.join(self.current_video_folder, filename)
        cap = cv2.VideoCapture(video_path)

        while True:
            self.disable_options = True
            ret, frame = cap.read()
            if not ret:
                break

            # Resize the frame to fit the display
            resized_frame = cv2.resize(frame, (self.video_width, self.video_height))

            # Convert the frame to RGB format compatible with Tkinter
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

            # Convert the RGB frame to a PhotoImage object
            self.last_img = ImageTk.PhotoImage(image=Image.fromarray(rgb_frame))

            # Update the label to show the new frame
            self.video_label.config(image=self.last_img)
            self.root.update()

        cap.release()
        self.disable_options = False

        



    def show_right_option(self, answer="None"):

        self.destroy_option_buttons()
        self.root.config(bg=self.bg_color)
        self.create_option_buttons()
        # play the audio of the right option
        self.play_audio(answer + ".mp3")
        for i, button in enumerate(self.option_buttons):
            if self.option_labels[i] != answer:
                button.destroy()
        
        if self.current_section == 0:
            pass
        else:
            self.replay_video()
        self.disable_options = True

        
        self.create_next_button()
        self.root.update()


    def select_option(self, option_label):
        if self.disable_options:
            return
        if self.has_timer:
            response_time = time.time() - self.start_time
            print(response_time)
        self.disable_options = True
        if self.has_replay:
            self.replay_button.destroy()
        # Record participant's choice (option_index)
        # don't displat the options buttons except the selected one but keep it in the same place
        # show the 'next' button at the right upper corner of the screen
        # console the option_index
        print(option_label)
        if self.current_section == 3:
            # don't show correct answer when testing
            self.load_next_video()
            # print("testing")
            return
        emoji = tk.Label(self.root, text="...", font=('Helvetica', '50'), bg=self.bg_color)
        emoji_place_x = 0
        emoji_place_y = 0
        for i, button in enumerate(self.option_buttons):
            if self.option_labels[i] == option_label:
                emoji_place_x = button.winfo_x() + button.winfo_width() / 2 - 20
                emoji_place_y = button.winfo_y() - button.winfo_height() / 2
                if (self.current_section == 0):
                    if (option_label == self.training_key[self.current_trial_index - 1]):
                        emoji.config(text="😃", bg="green")
                        self.root.config(bg="green")
                    else:
                        emoji.config(text="☹️", bg="red")
                        self.root.config(bg="red")
                else:
                    if (option_label == self.answer_key[self.current_trial_index - 1]):
                        emoji.config(text="😃", bg="green")
                        self.root.config(bg="green")
                    else:
                        emoji.config(text="☹️", bg="red")
                        self.root.config(bg="red")
            else:
                button.destroy()
        emoji.place(x=emoji_place_x, y=emoji_place_y, anchor="center")
        self.root.update()
        self.root.after(3000)
        if emoji:
            emoji.destroy()
        if self.current_section == 0:
            self.show_right_option(self.training_key[self.current_trial_index - 1])
        else:
            self.show_right_option(self.answer_key[self.current_trial_index - 1])


    def end_experiment(self):
        # Display a message or perform any necessary cleanup
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExperimentApp(root)
    root.mainloop()



"""
 pyinstaller --windowed --add-data "videos/training:videos/training" --add-data "videos/broad:videos/broad" --add-data "videos/narrow:videos/narrow" --add-data "videos/broad_test:videos/broad_test" --add-data "videos/narrow_test:videos/narrow_test" --add-data "audios:audios" --add-data "panels:panels" --add-data "catlearning.py:." catlearning.py
"""
