# Import all libraries
import sys
import os
import gi
import requests
from moviepy.editor import *
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Adw, GLib, Gst, GObject, Gio
from pytube import YouTube
from pathlib import Path
from pygame import*

playingMusic = False

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create GUI
        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.mainBox)

        self.mainBox.set_spacing(10)
        self.mainBox.set_margin_top(10)
        self.mainBox.set_margin_bottom(10)
        self.mainBox.set_margin_start(10)
        self.mainBox.set_margin_end(10)

        self.musicUrlBox = Gtk.Entry(text="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.mainBox.append(self.musicUrlBox)

        self.musicName = Gtk.Label()
        self.mainBox.append(self.musicName)
        self.musicName.set_text("Idling")

        self.songImage = Gtk.Picture()
        self.mainBox.append(self.songImage)

        self.downloadButton = Gtk.Button(label="Download")
        self.mainBox.append(self.downloadButton)
        self.downloadButton.connect('clicked', self.DownloadMusic)

        # Play/Stop button
        self.playStopButton = Gtk.Button(label="Play")
        self.mainBox.append(self.playStopButton)
        self.playStopButton.connect('clicked', self.PlayStopMusic)

        self.volumeSlider = Gtk.Scale()
        self.mainBox.append(self.volumeSlider)
        self.volumeSlider.set_digits(0)
        self.volumeSlider.set_range(0, 100)
        self.volumeSlider.set_draw_value(True)
        self.volumeSlider.set_value(100)
        self.volumeSlider.connect('value-changed', self.VolumeChanged)

        self.set_default_size(600, 370)
        self.set_title("Music Player")

    def DownloadMusic(self, button):
        # Download the music from YouTube using pytube
        url = self.musicUrlBox.get_text()
        print("Playing " + url)
        yt = YouTube(url)
        ys = yt.streams.get_by_itag("140")
        out_file = ys.download()
        # Convert the mp4 file to mp3 using moviepy
        audioclip = AudioFileClip(out_file)
        audioclip.write_audiofile("cache.mp3")
        audioclip.close()
        os.remove(out_file)
        # Play the mp3 file
        mixer.init()
        mixer.music.load("cache.mp3")
        mixer.music.play()

        # Set metadata
        # Title
        self.musicName.set_text(yt.title)
        # Cover art
        filename = Path("imgcache.jpg")
        response = requests.get(yt.thumbnail_url)
        filename.write_bytes(response.content)
        self.songImage.set_file(Gio.file_new_for_path("imgcache.jpg"))

        self.playStopButton.set_label("Pause")

    def PlayStopMusic(self, button):
        global playingMusic
        # Stop Music
        if playingMusic is True:
            mixer.music.pause()
            self.playStopButton.set_label("Play")
            playingMusic = False
        else:
            playingMusic = True
            self.playStopButton.set_label("Pause")
            mixer.music.unpause()

    def VolumeChanged(self, slider):
        volumePercentage = int(slider.get_value()) / 100
        mixer.music.set_volume(volumePercentage)

class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

app = MyApp(application_id="com.example.GtkApplication")
app.run(sys.argv)