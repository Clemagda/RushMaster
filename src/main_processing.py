from analyse_qualite import run_quality_analysis
from generation_resume import run_inference
import os
from transcription_audio import run_transcription

def process_video(video_path, output_dir, language):
    """Traite une vidéo et retourne les résultats sous forme de dictionnaire."""
    quality_analysis = run_quality_analysis(video_path)
    audio_transcription = run_transcription(video_path, language)
    video_summary = run_inference(video_path)
    
    result = {
        'video_id': os.path.basename(video_path),
        'Flou': quality_analysis.get('Flou', 'N/A'),
        'Frames floues': f"{quality_analysis.get('Pourcentage_flou', 0) * 100:.2f}%",
        'Stabilite': quality_analysis.get('Stabilité', 'N/A'),
        'Surexposition': quality_analysis.get('Frames_surexposees', 'N/A'),
        'Sous exposition' : quality_analysis.get('Frames_sousexposees', 'N/A'),
        'compression': quality_analysis.get('Compression', 'N/A'),
        'Qualité audio': quality_analysis.get('Audio','N/A'),
        'Transcription audio': audio_transcription,
        'Resume video': video_summary
    }
    return result


if __name__ == "__main__":
    process_video()