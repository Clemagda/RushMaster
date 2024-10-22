from analyse_qualite import run_quality_analysis
from generation_resume import run_inference
import os
from transcription_audio import run_transcription

def process_video(video_path, output_dir, language):
    """Traite une vidéo et retourne les résultats sous forme de dictionnaire."""
    video_id = os.path.basename(video_path).split('.')[0]
    quality_analysis = run_quality_analysis(video_path)
    audio_transcription = run_transcription(video_path, language)
    video_summary = run_inference(video_path, output_dir)
    return {
        'video_id': video_id,
        'quality_analysis': quality_analysis,
        'audio_transcription': audio_transcription,
        'video_summary': video_summary
    }

if __name__ == "__main__":
    process_video()