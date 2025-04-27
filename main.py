import os
import yt_dlp
import shutil
import time
import moviepy.editor as mp
import ffmpeg
import sounddevice as sd
from scipy.io.wavfile import write
import wave
import demucs.separate
from audio_similarity import AudioSimilarity
#moviepy==1.0.3


#idk if this adding dll medthod works for others too
os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")
import vlc

               
from yt_dlp import YoutubeDL
inurl = input("Lyric video url:")
url = [inurl]
with YoutubeDL() as ydl:
    ydl.download(url)

cur_dir = os.getcwd()
dlviddir = cur_dir + "/dlvid"
recwavdir = cur_dir + "/recwav"

#func to get mp4's dir
def mp4dir(x):
    for root, dirs, files in os.walk(x):
        for file in files: 
            if file.endswith('.mp4'):
                return root+'/'+str(file)

dlmp4 = mp4dir(cur_dir)

#move downloaded file
shutil.move(dlmp4, "./dlvid")
indlvid = mp4dir("./dlvid")

vid = mp.VideoFileClip(indlvid)
vid.audio.write_audiofile("./owav/output.wav", codec="pcm_s16le")
vid.audio.write_audiofile("./owav/output.mp3")


# time.sleep(5)
# os.remove("./owav/output.wav")

newmp4dir = mp4dir(dlviddir)

#find duration of song, but approximates the duration becuase float is changed into int
def get_duration_wave(file_path):
   with wave.open(file_path, 'r') as audio_file:
      frame_rate = audio_file.getframerate()
      n_frames = audio_file.getnframes()
      duration = n_frames / float(frame_rate)
      return duration
file_path = cur_dir + "/owav/output.wav"
duration = get_duration_wave(file_path)
print(duration)

#recording audio
fs = 44100

#this might differ for other when they run this code
sd.default.device = [2, 4]

#for testing
# duration = 5

#vlc start
songvideo = vlc.MediaPlayer(str(newmp4dir))
songvideo.play()

#rec start
recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)

#vlc, must add vlc media player to system variables
time.sleep(duration)
write(recwavdir + "/recordedaudio.wav", fs, recording)
songvideo.stop()

#demucs
songwavdir = cur_dir + "/owav/output.mp3"
demucs.separate.main(["--mp3", "--two-stems", "vocals", "-n", "mdx_extra", songwavdir])

#audio similarity

original_path = cur_dir + "/recwav"
compare_path = cur_dir + "/separated/mdx_extra/output/vocals.mp3"

sample_rate = 44100
weights = {
    'zcr_similarity': 0.2,
    'rhythm_similarity': 0.2,
    'chroma_similarity': 0.2,
    'energy_envelope_similarity': 0.1,
    'spectral_contrast_similarity': 0.1,
    'perceptual_similarity': 0.2
}

sample_size = 1
verbose = True
audio_similarity = AudioSimilarity(original_path, compare_path, sample_rate, weights, verbose=verbose, sample_size=sample_size)
similarity_score = audio_similarity.stent_weighted_audio_similarity(metrics='all')

totalsim = sum(similarity_score.values())
simpercentage = str(int(totalsim/7*100))

print(simpercentage + "%" + " similar")

#func to remove things in a folder
def delete_files_in_directory(directory_path):
    files = os.listdir(directory_path)
    for file in files:
        file_path = os.path.join(directory_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

os.system(cur_dir + "/separated/mdx_extra/output/no_vocals.mp3")
os.system(cur_dir + "/recwav/recordedaudio.wav")
songvideo.audio_set_mute(True)
songvideo.play()
time.sleep(duration)
songvideo.stop()

#cleaning shif up
delete_files_in_directory(cur_dir + "/owav")
delete_files_in_directory(cur_dir + "/recwav")
delete_files_in_directory(cur_dir + "/separated/mdx_extra")
delete_files_in_directory(cur_dir + "/dlvid")

# #new video using mp, work in progress
# no_vocal = cur_dir + "/separated/mdx_extra/output/no_vocals.mp3"
# audioclip = mp.AudioFileClip(cur_dir + "/recwav/recordedaudio.wav")
# audioclipmp3 = audioclip.write_audiofile(cur_dir + "/recordedaudio.mp3")
# audioclipmp3dir = cur_dir + "/recordedaudio.mp3"
# strnewmp4dir = str(newmp4dir)
# print(strnewmp4dir)
# videoclip = mp.VideoFileClip(strnewmp4dir)
# # ffmpeg.output(videoclip.video, audioclipmp3dir.audio, "./finishedVid.mp4", codec='copy').overwrite_output().run(quiet=True)
# ffmpeg.concat(videoclip, audioclipmp3dir, v=1, a=1).output('./processed_folder/finished_video.mp4').run()