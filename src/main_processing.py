from analyse_qualite import run_quality_analysis
from generation_resume import run_inference
from transcription_audio import run_transcription

def process_video(video_path, output_dir, language):
    quality_analysis = run_quality_analysis(video_path)
    audio_transcription = run_transcription(video_path, language)
    video_summary = run_inference(video_path, output_dir)
    return {
        'quality_analysis': quality_analysis,
        'audio_transcription': audio_transcription,
        'video_summary': video_summary
    }

if __name__ == "__main__":
    process_video()