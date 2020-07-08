from pytube import YouTube

vid = YouTube("https://www.youtube.com/watch?v=ER5JYFKkYDg")
#.streams.get_highest_resolution.download()

#playlist = Playlist("link")
#for video in playlist:
#video.streams.get_highest_resolution().download()

#vid.streams[0].download()

print(vid.streams.filter(progressive=True))