try:
    from .pygit2_impl import get_head_sha1
except ImportError:
    from .subprocess_impl import get_head_sha1
