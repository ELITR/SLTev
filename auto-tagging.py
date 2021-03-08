# tagging into the SLTev repo (https://github.com/ELITR/SLTev.git)

import git
from SLTev import __version__

repo = git.Repo(".")
new_tag = repo.create_tag(__version__, message='Tagging version "{0}"'.format(__version__))

repo.remotes.origin.push(new_tag)
