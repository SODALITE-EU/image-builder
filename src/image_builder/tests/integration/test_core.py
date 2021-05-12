import pytest


@pytest.mark.parametrize('test_name', [
    'test_01_tar',
    'test_02_no_context',
    'test_03_build_context',
    'test_04_image_variants',
    'test_05_subdir_context',
    'test_06_git',
    'test_07_git_workdir_dockerfile'
])
def test_integration(core_test_tools, test_name):
    # unpack test tools
    run_test, check_docker_image = core_test_tools

    # run test
    exit_code = run_test(test_name)
    assert exit_code == 0

    check_docker_image(test_name)




