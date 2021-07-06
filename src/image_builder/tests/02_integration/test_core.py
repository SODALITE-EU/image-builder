import pytest
from pathlib import Path

# New integration tests for ImageBuilder API - ImageBuilder blueprint integration can be added
# to 'build_params' dir.


def discover_tests():
    """
    discovers build params for testing

    """
    build_params = Path(__file__).parent / 'build_params'
    return [file.name.replace('.json', '') for file in build_params.glob('*.json')]


@pytest.mark.parametrize('test_name', discover_tests())
def test_integration(core_test_tools, test_name):
    # unpack test tools
    run_test, check_docker_image = core_test_tools

    # run test
    exit_code = run_test(test_name)
    assert exit_code == 0

    check_docker_image(test_name)
