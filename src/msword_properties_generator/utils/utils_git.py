from git import Repo, Actor, exc
import logging
import git
import os


def git_stage_commit_push(file_path: str, commit_message: str = "Automated commit and push"):
    repo_path = get_repo_root()
    repo = Repo(repo_path)
    bot_author = Actor("github-actions[bot]", "github-actions[bot]@users.noreply.github.com")

    relative_file_path = os.path.relpath(file_path, repo_path)

    try:
        full_path = os.path.join(repo_path, relative_file_path)

        if os.path.exists(full_path):
            # File exists, stage addition or modification clearly
            repo.index.add([relative_file_path])
            logging.debug(f"📥 File staged explicitly for addition/update: {relative_file_path}")
        else:
            # File doesn't exist, fully stage removal via git CLI
            repo.git.rm(relative_file_path)
            logging.debug(f"📥 File staged explicitly for removal: {relative_file_path}")

        # commit staged changes
        repo.index.commit(commit_message, author=bot_author, committer=bot_author)
        logging.debug(f"📝 Committed to Git of: {relative_file_path} w commit message: '{commit_message}'")

        # push & verify the push
        origin = repo.remote('origin')
        push_result = origin.push()[0]
        if push_result.flags & push_result.ERROR:
            logging.error(f"❌ Push failed: {push_result.summary}")
            raise RuntimeError(f"❌ Push failed: {push_result.summary}")
        logging.info(f"🚀 Git push successful: {relative_file_path}")

    except exc.GitCommandError as e:
        logging.error(f"❌ Git command error: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"❌ unexpected error: {str(e)}")
        raise

def get_repo_root():
    repo = git.Repo('.', search_parent_directories=True)
    repo_root = repo.git.rev_parse("--show-toplevel")
    return repo_root
