import pytest
from src.analyse_qualite import detect_flou, detect_exposition, detect_compression_excessive, analyser_niveaux_sonores


def test_detect_flou():
    result, pourcentage = detect_flou("tests/videos/video_floue.mp4")
    assert isinstance(result, bool)
    assert pourcentage >= 0


def test_detect_exposition():
    result = detect_exposition("tests/videos/video_exposition.mp4")
    assert 'pourcentage_sous_exposees' in result
    assert 'pourcentage_surexposees' in result


def test_detect_compression_excessive():
    result = detect_compression_excessive(
        "tests/videos/video_audio.mp4")
    assert isinstance(result, bool)


def test_analyser_niveaux_sonores():
    result = analyser_niveaux_sonores("tests/videos/video_audio.mp4")
    assert 'pourcentage_faible' in result
    assert 'pourcentage_sature' in result
