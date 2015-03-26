from tags.git import pygit2_impl, subprocess_impl

def test_pygit2_impl(run_git_tests):
    run_git_tests(pygit2_impl)

def test_subprocess_impl(run_git_tests):
    run_git_tests(subprocess_impl)
