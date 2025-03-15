import argparse
from voice_processing.voice_recorder import VoiceSampleCreator
from voice_processing.tts_generator import TTSEngine
from nlp_processing.text_analyzer import ScriptProcessor
from minecraft_agent.action_executor import ActionController
from video_processing.video_composer import VideoProducer
import yaml
import os

def main():
    # Setup environment
    with open("config/settings.yaml") as f:
        config = yaml.safe_load(f)
        
    os.makedirs(config['project']['output_dir'], exist_ok=True)
    
    # Voice sample creation
    if not os.listdir(config['project']['voice_samples_dir']):
        print("No voice samples found. Starting recording process...")
        VoiceSampleCreator().create_samples()
    
    # Process script
    processor = ScriptProcessor()
    analysis = processor.analyze("script.txt")
    
    # Generate audio
    tts = TTSEngine()
    audio_path = tts.generate_audio(analysis['text'])
    
    # Generate gameplay
    miner = ActionController()
    frames = miner.execute_script(analysis['actions'], analysis['duration'])
    
    # Create video
    producer = VideoProducer()
    producer.create_video(frames, audio_path, analysis['subtitles'])
    
    print("\nVideo creation completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", required=True, help="Path to script file")
    args = parser.parse_args()
    main()
