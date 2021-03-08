# tagging into the SLTev repo (https://github.com/ELITR/SLTev.git)

import git
from SLTev import __version__

repo = git.Repo(".")
tag = "v" + __version__
new_tag = repo.create_tag(tag, message='Tagging version "{0}"'.format(__version__))

repo.remotes.origin.push(new_tag)
