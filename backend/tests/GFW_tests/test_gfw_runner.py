from unittest.mock import patch, call
import backend.processors.gfw.gfw_runner as gfw_runner
import sys

@patch("backend.processors.gfw.gfw_runner.time.sleep", side_effect=KeyboardInterrupt)
@patch("backend.processors.gfw.gfw_runner.subprocess.run")
def test_gfw_runner_main(mock_run, mock_sleep):
    gfw_runner.scripts = ["backend.processors.gfw.test_script1", "backend.processors.gfw.test_script2"]

    try:
        gfw_runner.main()
    except KeyboardInterrupt:
        pass

    expected_calls = [
        call([sys.executable, "-m", "backend.processors.gfw.test_script1"]),
        call([sys.executable, "-m", "backend.processors.gfw.test_script2"])
    ]
    mock_run.assert_has_calls(expected_calls)
    mock_sleep.assert_called_once_with(300)