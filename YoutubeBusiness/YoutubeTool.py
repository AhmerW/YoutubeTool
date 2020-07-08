import os 
import random
import requests
import re

from pytube import YouTube, Playlist
from datetime import datetime
from tkinter import (
    Tk,
    Button,
    Entry,
    Frame,
    Label,
    Checkbutton,
    Toplevel,
    ttk,
    IntVar,
    HORIZONTAL,
    END,
    NORMAL,
    DISABLED
    
    
)
"""
TO - DO 

#three classes
    login
    Downloader
    MainWindow
    
Tkinter:
    Login??
    ------
    Color:
        Red / Orange - ish
        
    ProgressBar?
    
    FirstFrame:
        OneEntry -> inputs the youtube video
        
        Buttons:
            "Download Youtube video"
            "Download playlist?"
                -> Opens a new window 'options??' -> choose resultion etc
                -> have a check "automatically download highest resolution?"
                
"""

class Login(object):
    def __new__(self):
        raise NotImplementedError("Not implemented class")

class Downloader(object):
    def __init__(self):
        self.download_path = os.path.join(os.getcwd(), 'downloads')
        self.got_proxies = False 
        
        self.proxies = {
            
        }
    
    def get_proxies(self):
        try:
            r = requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=https&anonymity=elite")
            data = str(r.text).split('\n')
            for value in data:
                host, port = value.split(':')
                self.proxies[host] = port
            
        except:
            pass
        
    def download(self, video, use_highest=True):


        title = video.title
        if not title.endswith('.mp4'):
            check_title = str(title)+".mp4"
        else:
            check_title = str(title)
        if check_title in os.listdir(self.download_path):
            title = title+str(random.randint(1, 9999))
        status = True 
        try:
            if use_highest:
                _ = video.streams.get_highest_resolution().download(self.download_path, title)
            else:
                _ = video.streams[0].download(self.download_path, title)
                
    
        except Exception as e:
            print(e)
            status = False
            
        return [title, status, "none", "none"]
    
    def downloadVideo(self, _path, use_highest=True, playlist=False):
        if not self.got_proxies:
            self.get_proxies()
        if os.path.isfile(_path):
            try:
                link = open(_path, 'r').read().splitlines()
            except FileNotFoundError:
                link = [str(_path)]
        else:
            link = [str(_path)]
          
        result = []

        for _link in link:
            try:
                if playlist:
                    video = Playlist(_link, proxies=self.proxies)
                    video._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
                    for vid in video:
                        vid = YouTube(vid, proxies=self.proxies)
                        res = self.download(vid, use_highest=use_highest)
                        result.append(res)
                else:
                    video = YouTube(_link, proxies=self.proxies)
                    res = self.download(video, use_highest=use_highest)
                    result.append(res)
            except Exception as e:
                print(e)
                result.append([_link, False, None, 0])

        return result


class MainWindow(object):
    def __init__(self):
        #downloader obj
        self.downloader = Downloader()
        #time launched at
        self.started_at = datetime.now()
        
        #window object 
        self.master = Tk()
        
        # self.width, self.heigth = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        
        #configure values
        self.master.winfo_toplevel().title("YoutubeTool")
        self.master.geometry("800x600")
        self.master.resizable(0, 0)
        
        #colors
        self.master.configure(bg='#e0ddda')
        
        #status
        self.download_highest_resolution = IntVar()
        self.download_highest_resolution.set(1)
        
        #for keeping track of the current downloads label
        self.current_y = 400
        self.current_x = 0
        self.total_downloads = 1
        
        #all downloaded now labels
        self.downloaded_now_labels = []
    

    def rgb(self, _rgb): return "#%02x%02x%02x" % _rgb 
    
    def start_downloading(self, playlist=False):
        data = str(self.entry_main.get()).strip()
        self.entry_main.delete(0, END)
        
        result = self.downloader.downloadVideo(
            data, 
            use_highest=bool(self.download_highest_resolution),
            playlist=playlist
        )
        
        for value in result:
            value, status, _, _ = value
            if self.current_y >= 550:
                self.current_y = 425
                self.current_x += 150
            color = self.rgb((0, 200, 0))
            if not status:
                color = self.rgb((200, 0, 0))
            label = Label(
                self.master, 
                text=f"[{self.total_downloads}] Downloaded: {value}",
                bg=color,
                fg=self.rgb((0, 0, 0))
                )
            
            label.place(
                x=self.current_x,
                y=self.current_y
            )
            
            
            
            self.current_y += 35
            self.total_downloads += 1
            self.downloaded_now_labels.append(label)
            
    def clear_current_downloads(self):
        self.current_x = 0
        self.current_y = 425
        for label in self.downloaded_now_labels:
            label.destroy()
            
    def show_settings(self):
        top = Toplevel()
        top.title("Settings")
        top.geometry("300x300")
        top.resizable(0, 0)
        
        ## create widgets
        main_label = Label(
            top, 
            text="Settings for YoutubeTool", 
            bg=self.rgb((255, 0, 0))
            
        )
        main_label.place(x=0, y=0, width=300, height=50)
        
        check = Checkbutton(
            top, 
            text="Download highest resolution", 
            variable=self.download_highest_resolution,
            onvalue=1, offvalue=0,
            bg='#bab7b5'
            
        )
        check.place(x=0, y=75, width=300, height=50)
        
        _clear = Button(
            top,
            text="Clear current downloads",
            bg='#bab7b5',
            command=self.clear_current_downloads
        )
        
        _clear.place(x=0, y=150, width=300, height=50)

        top.mainloop()
    
    def enable_entry(self, event):
        try:
            self.entry_main.configure(state=NORMAL)
            self.entry_main.unbind('<Button-1>', self.on_click_id)
            self.entry_main.delete(0, END)
        except:
            pass
        
    def enter_button(self, event = None): self.button_downloadVideo.configure(bg=self.rgb((255, 0, 0)))
    def leave_button(self, event = None): self.button_downloadVideo.configure(bg=self.rgb((230, 0, 0)))
    def enter_button2(self, event = None): self.button_downloadPlaylist.configure(bg=self.rgb((255, 0, 0)))
    def leave_button2(self, event = None): self.button_downloadPlaylist.configure(bg=self.rgb((230, 0, 0)))

    def _create_widgets(self):
        ## ENTRIES
        self.entry_main = Entry(
            self.master, 
            bg=self.rgb((255, 0, 0)),

        )
        self.entry_main.insert(0, "Type in a link to video, playlist or a txt file")
        self.entry_main.configure(state=DISABLED)
        self.on_click_id = self.entry_main.bind('<Button-1>', self.enable_entry)
        
        
        ## BUTTONS
        
        self.button_settings = Button(
            self.master,
            text="Settings",
            bg='#bab7b5',
            command=self.show_settings
        )
        
        self.button_downloadVideo = Button(
            self.master, 
            text="Download Video", 
            bg=self.rgb((230, 0, 0)),
            command=self.start_downloading
        )
        
        self.button_downloadVideo.bind("<Enter>", self.enter_button)
        self.button_downloadVideo.bind("<Leave>", self.leave_button)

        self.button_downloadPlaylist = Button(
            self.master, 
            text="Download Playlist", 
            bg=self.rgb((230, 0, 0)),
            command = lambda : self.start_downloading(playlist=True)
        )
    
        self.button_downloadPlaylist.bind("<Enter>", self.enter_button2)
        self.button_downloadPlaylist.bind("<Leave>", self.leave_button2)
        
        
        self.current_downloads = Label(
            self.master,
            bg=self.rgb((0, 0, 0)),
            fg=self.rgb((0, 255, 0))
            
        )
    
    def _place_all_widgets(self):
        ## ENTRIES 
        self.entry_main.place(
            x=200, 
            y=50,
            height=40,
            width=400
            )
        
        ## BUTTONS
        
        #settings button
        self.button_settings.place(
            x=650,
            y=00,
            height=20,
            width=150
        )
        
        #download video button
        self.button_downloadVideo.place(
            x=245,
            y=150,
            height=65,
            width=300
        )
        
        #download playlist button
        self.button_downloadPlaylist.place(
            x=245,
            y=250,
            height=65,
            width=300
        )
        #current downloads label
        self.current_downloads.place(
            x=0, 
            y=self.current_y,
            height=20,
            width=900
        )
        self.current_y += 25
    
    def start_and_run(self):
        self._create_widgets()
        self._place_all_widgets()
        
        self.master.mainloop()

if __name__ == "__main__":
    Main = MainWindow()
    
    Main.start_and_run()