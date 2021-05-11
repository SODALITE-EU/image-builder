

def test_01_tar(core_test_tools):
    # unpack test tools
    run_test, check_docker_image = core_test_tools

    # run test
    test_name = 'test_01_tar'
    exit_code = run_test(test_name)
    assert exit_code == 0

    check_docker_image(test_name)


def test_02_no_context(core_test_tools):
    # unpack test tools
    run_test, check_docker_image = core_test_tools

    # run test
    test_name = 'test_02_no_context'
    exit_code = run_test(test_name)
    assert exit_code == 0

    check_docker_image(test_name)


def test_03_build_context(core_test_tools):
    # unpack test tools
    run_test, check_docker_image = core_test_tools

    # run test
    test_name = 'test_03_build_context'
    exit_code = run_test(test_name)
    assert exit_code == 0

    check_docker_image(test_name)


def test_04_image_variants(core_test_tools):
    # unpack test tools
    run_test, check_docker_image = core_test_tools

    # run test
    test_name = 'test_04_image_variants'
    exit_code = run_test(test_name)
    assert exit_code == 0

    check_docker_image(test_name)


def test_05_subdir_context(core_test_tools):
    # unpack test tools
    run_test, check_docker_image = core_test_tools

    # run test
    test_name = 'test_05_subdir_context'
    exit_code = run_test(test_name)
    assert exit_code == 0

    check_docker_image(test_name)

def test_06_git(core_test_tools):
    # unpack test tools
    run_test, check_docker_image = core_test_tools

    # run test
    test_name = 'test_06_git'
    exit_code = run_test(test_name)
    assert exit_code == 0

    check_docker_image(test_name)

def test_07_git_workdir_dockerfile(core_test_tools):
    # unpack test tools
    run_test, check_docker_image = core_test_tools

    # run test
    test_name = 'test_07_git_workdir_dockerfile'
    exit_code = run_test(test_name)
    assert exit_code == 0

    check_docker_image(test_name)



