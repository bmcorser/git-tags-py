from tags import git


def test_get_tag_list(session_repo):
    retval = git.get_tag_list()
    assert retval == ['a', 'b']

def test_cli_tag_exists(session_repo):
    tags.git.create_tag('abc', 'message')
    tags.git.create_tag('abc', 'message')
