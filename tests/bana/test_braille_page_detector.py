from brf2ebrf.bana import PageNumberPosition, create_braille_page_detector
from brf2ebrf.parser import DetectionResult


def test_find_first_page():
    page_detector = create_braille_page_detector()
    brf = "TE/ BRF\nEXTRA TEXT\f"
    actual = page_detector(brf, 0, "StartBraillePage", "")
    expected_brf = "\ue000{\"BraillePage\": {}}\ue001" + brf.rstrip("\f")
    expected = DetectionResult(len(brf), "StartBraillePage", 1.0, expected_brf)
    assert actual == expected


def test_assume_all_is_page_when_no_form_feed():
    brf = "TE/ TEXT\nEXTRA TEXT"
    expected = DetectionResult(text="\ue000{\"BraillePage\": {}}\ue001" + brf, cursor=len(brf),
                               state="StartBraillePage", confidence=1.0)
    actual = create_braille_page_detector()(brf, 0, "StartBraillePage", "")
    assert actual == expected


def test_when_state_does_not_apply():
    expected = DetectionResult(1, "OtherState", 0.0, "T")
    brf = "TE/ TEXT\nEXTRA TEXT\f"
    actual = create_braille_page_detector()(brf, 0, "OtherState", "")
    assert actual == expected


def test_detect_braille_page_number():
    brf = "\n".join(["TE/ TEXT"] * 25)
    expected_brf = "\ue000{\"BraillePage\": {\"Number\": \"#A\"}}\ue001" + brf
    brf += (" " * 30) + "#A"
    expected = DetectionResult(len(brf), "StartBraillePage", 1.0, expected_brf)
    actual = create_braille_page_detector(number_position=PageNumberPosition.BOTTOM_RIGHT)(brf, 0, "StartBraillePage", "")
    assert actual == expected
