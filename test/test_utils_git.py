from msword_properties_generator.utils.utils_git import git_stage_commit_push, get_repo_root
from unittest.mock import patch, MagicMock
from git import exc
import unittest
import tempfile
import os


class TestUtilsGit(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        self.repo_root = self.temp_dir
        
        self.test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(self.test_file, 'w') as f:
            f.write('test content')
            
        self.logging_patcher = patch('msword_properties_generator.utils.utils_git.logging')
        self.mock_logging = self.logging_patcher.start()

    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
        
        # Stop all patchers
        self.logging_patcher.stop()

    @patch("msword_properties_generator.utils.utils_git.get_private_assets_repo")
    @patch('msword_properties_generator.utils.utils_git.get_repo_root')
    @patch('msword_properties_generator.utils.utils_git.Repo')
    def test_git_stage_commit_push_new_file(self, mock_repo_class, mock_get_repo_root, get_private_assets_repo):
        mock_get_repo_root.return_value = self.repo_root
        mock_repo = MagicMock()
        mock_repo.working_tree_dir = self.repo_root
        mock_repo_class.return_value = mock_repo
        get_private_assets_repo.return_value = mock_repo

        # Mock the remote and push
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote
        mock_push_result = MagicMock()
        mock_push_result.flags = 0  # No error
        mock_push_result.ERROR = 1  # Define ERROR flag
        mock_push_result.summary = "Success"
        mock_remote.push.return_value = [mock_push_result]
        
        # Call the function
        git_stage_commit_push(self.test_file, "Test commit message")
        
        # Verify the calls
        mock_repo.index.add.assert_called_once_with([self.test_file])
        mock_repo.index.commit.assert_called_once()
        mock_remote.push.assert_called_once()
        
        # Verify logging
        self.mock_logging.debug.assert_any_call(f"📥 File staged explicitly for addition/update: {self.test_file}")
        self.mock_logging.debug.assert_any_call(f"📝 Committed to Git of: {self.test_file} w commit message: 'Test commit message'")
        self.mock_logging.info.assert_called_with(f"🚀 Git push successful: {self.test_file}")

    @patch("msword_properties_generator.utils.utils_git.get_private_assets_repo")
    @patch('msword_properties_generator.utils.utils_git.get_repo_root')
    @patch('msword_properties_generator.utils.utils_git.Repo')
    def test_git_stage_commit_push_delete_file(self, mock_repo_class, mock_get_repo_root, get_private_assets_repo):
        mock_get_repo_root.return_value = self.repo_root
        mock_repo = MagicMock()
        mock_repo.working_tree_dir = self.repo_root
        mock_repo_class.return_value = mock_repo
        get_private_assets_repo.return_value = mock_repo

        # Mock the remote and push
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote
        mock_push_result = MagicMock()
        mock_push_result.flags = 0  # No error
        mock_push_result.ERROR = 1  # Define ERROR flag
        mock_push_result.summary = "Success"
        mock_remote.push.return_value = [mock_push_result]
        
        # Delete the test file
        os.remove(self.test_file)
        
        # Call the function
        git_stage_commit_push(self.test_file, "Test delete commit")
        
        # Verify the calls
        mock_repo.git.rm.assert_called_once_with(self.test_file)
        mock_repo.index.commit.assert_called_once()
        mock_remote.push.assert_called_once()
        
        # Verify logging
        self.mock_logging.debug.assert_any_call(f"📥 File staged explicitly for removal: {self.test_file}")
        self.mock_logging.debug.assert_any_call(f"📝 Committed to Git of: {self.test_file} w commit message: 'Test delete commit'")
        self.mock_logging.info.assert_called_with(f"🚀 Git push successful: {self.test_file}")

    @patch('msword_properties_generator.utils.utils_git.get_repo_root')
    @patch('msword_properties_generator.utils.utils_git.Repo')
    def test_git_stage_commit_push_push_error(self, mock_repo_class, mock_get_repo_root):
        mock_get_repo_root.return_value = self.repo_root
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        # Mock the remote and push with error
        mock_remote = MagicMock()
        mock_repo.remote.return_value = mock_remote
        mock_push_result = MagicMock()
        mock_push_result.flags = 1  # Error flag
        mock_push_result.ERROR = 1  # Define ERROR flag
        mock_push_result.summary = "Push failed"
        mock_remote.push.return_value = [mock_push_result]
        
        # Call the function and expect exception
        with self.assertRaises(RuntimeError) as context:
            git_stage_commit_push(self.test_file)
        
        # Verify error message
        self.assertIn("❌ Push failed: Push failed", str(context.exception))
        
        # Verify logging - match the actual error message format
        self.mock_logging.error.assert_called_with("❌ unexpected error: ❌ Push failed: Push failed")

    @patch('msword_properties_generator.utils.utils_git.get_repo_root')
    @patch('msword_properties_generator.utils.utils_git.Repo')
    def test_git_stage_commit_push_git_command_error(self, mock_repo_class, mock_get_repo_root):
        mock_get_repo_root.return_value = self.repo_root
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo

        # Mock Git command error
        mock_repo.index.add.side_effect = exc.GitCommandError('git', 'add failed')
        
        # Call the function and expect exception
        with self.assertRaises(exc.GitCommandError):
            git_stage_commit_push(self.test_file)
        
        # Verify logging - the actual error message is different from what we expected
        self.mock_logging.error.assert_called_with("❌ Git command error: Cmd('git') failed due to: 'add failed'\n  cmdline: git")

    @patch('msword_properties_generator.utils.utils_git.git.Repo')  # Fix: patch the correct path
    def test_get_repo_root(self, mock_repo_class):
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        # Get the actual repository root for comparison
        actual_repo_root = os.path.normpath('C:/Projects/Github/msword-properties-generator')
        mock_repo.git.rev_parse.return_value = actual_repo_root
        
        # Call the function
        result = get_repo_root()
        
        # Verify result - normalize paths for comparison
        self.assertEqual(os.path.normpath(result), actual_repo_root)
        
        # Verify Repo was initialized correctly
        mock_repo_class.assert_called_once_with('.', search_parent_directories=True)
        mock_repo.git.rev_parse.assert_called_once_with("--show-toplevel")

if __name__ == '__main__':
    unittest.main() 