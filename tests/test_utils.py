import datetime

from main import baghdad_time


def test_baghdad_time_default():
    expected = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%I:%M %p")
    assert baghdad_time() == expected
