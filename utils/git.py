import sh

class GitUtils:
    
    def __init__(self):
        pass

        git = sh.git.bake(_cwd='/home/me/repodir')
        print(git.status())
        # checkout and track a remote branch
        print(git.checkout('-b', 'somebranch'))
        # add a file
        print(git.add('somefile'))
        # commit
        print(git.commit(m='my commit message'))
        # now we are one commit ahead
        print(git.status())
