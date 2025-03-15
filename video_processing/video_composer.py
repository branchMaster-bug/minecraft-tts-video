from moviepy.editor import *
import yaml
from PIL import Image, ImageDraw, ImageFont

class VideoProducer:
    def __init__(self):
        with open("config/settings.yaml") as f:
            self.config = yaml.safe_load(f)
            
        self.sub_style = self.config['video']['subtitle_style']
        
    def create_video(self, gameplay_frames, audio_path, subtitles):
        # Create video clip
        video_clip = ImageSequenceClip(gameplay_frames, fps=self.config['video']['fps'])
        
        # Add audio
        audio_clip = AudioFileClip(audio_path)
        video_clip = video_clip.set_audio(audio_clip)
        
        # Add subtitles
        sub_clips = self._create_subtitles(subtitles)
        final = CompositeVideoClip([video_clip] + sub_clips)
        
        # Render
        final.write_videofile("output/final_video.mp4", 
                            codec="libx264",
                            audio_codec="aac",
                            threads=8)
    
    def _create_subtitles(self, subtitles):
        clips = []
        for sub in subtitles:
            txt_clip = TextClip(sub['text'],
                              font=self.sub_style['font'],
                              fontsize=self.sub_style['size'],
                              color=self.sub_style['color'],
                              stroke_color=self.sub_style['stroke_color'],
                              stroke_width=self.sub_style['stroke_width'])
            txt_clip = txt_clip.set_position('center').set_duration(sub['duration'])
            clips.append(txt_clip)
        return clips
