"""Tests for the setup_badge CLI module."""

import json
from unittest.mock import MagicMock, patch

import git
import pytest
from click.testing import CliRunner

from setup_badge.cli import (
    check_badge_changes,
    check_hex_color,
    check_user_inputs,
    checkout_branch,
    create_badge_dict,
    create_badge_json,
    create_shieldsio_endpoint_badge,
    main,
    push_changes,
)


@pytest.fixture
def mock_repo():
    """Fixture for a mock git repository."""
    repo = MagicMock()
    repo.active_branch.name = "main"
    repo.heads = {}
    repo.remote.return_value.name = "origin"
    return repo


class TestCheckHexColor:
    def test_valid_6_digit_hex(self):
        assert check_hex_color("ff00aa") is True
        assert check_hex_color("FF00AA") is True
        assert check_hex_color("#ff00aa") is True
        assert check_hex_color("#FF00AA") is True

    def test_valid_3_digit_hex(self):
        assert check_hex_color("f0a") is True
        assert check_hex_color("F0A") is True
        assert check_hex_color("#f0a") is True
        assert check_hex_color("#F0A") is True

    def test_invalid_hex_color(self):
        assert check_hex_color("gg00aa") is False
        assert check_hex_color("12345") is False
        assert check_hex_color("1234567") is False
        assert check_hex_color("") is False

    def test_mixed_case_hex(self):
        assert check_hex_color("AbCdEf") is True
        assert check_hex_color("aBcDeF") is True


class TestCreateBadgeDict:
    def test_creates_correct_dict(self):
        result = create_badge_dict("flat", "test", "2e2e2e", "passing", "4c1")
        assert result == {
            "schemaVersion": 1,
            "style": "flat",
            "label": "test",
            "labelColor": "2e2e2e",
            "message": "passing",
            "color": "4c1",
        }

    def test_dict_has_all_required_keys(self):
        result = create_badge_dict("flat-square", "label", "abc", "msg", "def")
        assert set(result.keys()) == {"schemaVersion", "style", "label", "labelColor", "message", "color"}


class TestCheckUserInputs:
    def test_valid_inputs(self):
        result = check_user_inputs(["flat"], "flat", "https://example.com", "fff", "000")
        assert result is True

    def test_invalid_style(self):
        result = check_user_inputs(["flat"], "invalid", "https://example.com", "fff", "000")
        assert result is False

    def test_invalid_label_color(self):
        result = check_user_inputs(["flat"], "flat", "https://example.com", "invalid", "000")
        assert result is False

    def test_invalid_message_color(self):
        result = check_user_inputs(["flat"], "flat", "https://example.com", "fff", "not-a-color")
        assert result is False

    def test_empty_url_is_valid(self):
        result = check_user_inputs(["flat"], "flat", "", "fff", "000")
        assert result is True


class TestCreateBadgeJson:
    def test_creates_badges_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        badge_dict = {"schemaVersion": 1, "style": "flat", "label": "test", "message": "passing", "color": "4c1"}
        result = create_badge_json(badge_dict, "test")
        assert result is True
        assert (tmp_path / "badges").exists()
        assert (tmp_path / "badges" / "test.json").exists()

    def test_writes_valid_json(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        badge_dict = {
            "schemaVersion": 1,
            "style": "flat",
            "label": "test",
            "labelColor": "fff",
            "message": "passing",
            "color": "4c1",
        }
        create_badge_json(badge_dict, "test")
        with open(tmp_path / "badges" / "test.json") as f:
            data = json.load(f)
        assert data == badge_dict

    def test_writes_json_with_indentation(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        badge_dict = {"schemaVersion": 1, "style": "flat", "label": "test", "message": "passing", "color": "4c1"}
        create_badge_json(badge_dict, "test")
        content = (tmp_path / "badges" / "test.json").read_text()
        assert "\n" in content

    def test_invalid_dict_returns_false(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = create_badge_json("not-a-dict", "test")
        assert result is False

    def test_non_dict_input_no_file_created(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        create_badge_json(["list"], "test")
        assert not (tmp_path / "badges").exists()


class TestCheckBadgeChanges:
    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        return repo

    def test_returns_true_for_untracked_file(self, mock_repo):
        mock_repo.untracked_files = ["badges/new-badge.json"]
        mock_repo.git.diff.return_value = ""
        result = check_badge_changes(mock_repo, "new-badge")
        assert result is True

    def test_returns_true_for_modified_file(self, mock_repo):
        mock_repo.untracked_files = []
        mock_repo.git.diff.return_value = "diff"
        result = check_badge_changes(mock_repo, "test")
        assert result is True

    def test_returns_false_for_unchanged_file(self, mock_repo):
        mock_repo.untracked_files = []
        mock_repo.git.diff.return_value = ""
        result = check_badge_changes(mock_repo, "test")
        assert result is False


class TestCliIntegration:
    def setup_method(self):
        self.runner = CliRunner()

    def test_cli_shows_version(self):
        from setup_badge import __version__

        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_cli_shows_help(self):
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "CLI command to generate" in result.output
        assert "--badge-name" in result.output

    def test_cli_validates_badge_style(self):
        result = self.runner.invoke(main, ["--badge-style", "invalid"])
        assert result.exit_code == 1
        assert "one or more of your inputs failed validations" in result.output

    def test_cli_validates_hex_color(self):
        result = self.runner.invoke(main, ["--label-color", "not-a-color"])
        assert result.exit_code == 1
        assert "one or more of your inputs failed validations" in result.output


class TestCliEndToEnd:
    def setup_method(self):
        self.runner = CliRunner()

    @patch("setup_badge.cli.get_repo")
    @patch("setup_badge.cli.checkout_branch")
    @patch("setup_badge.cli.create_badge_dict")
    @patch("setup_badge.cli.create_badge_json")
    @patch("setup_badge.cli.check_badge_changes")
    @patch("setup_badge.cli.push_changes")
    @patch("setup_badge.cli.create_shieldsio_endpoint_badge")
    def test_cli_creates_badge_successfully(
        self, mock_eb, mock_push, mock_changes, mock_json, mock_dict, mock_checkout, mock_repo
    ):
        mock_repo_inst = MagicMock()
        mock_repo_inst.active_branch.name = "main"
        mock_repo.return_value = mock_repo_inst
        mock_checkout.return_value = True
        mock_dict.return_value = {"schemaVersion": 1}
        mock_json.return_value = True
        mock_changes.return_value = True
        mock_push.return_value = "abc123"
        mock_eb.return_value = "![test](https://img.shields.io/endpoint?url=...)"
        result = self.runner.invoke(
            main, ["--badge-name", "test-badge", "--badge-branch", "badges", "--badge-style", "flat"]
        )
        assert result.exit_code == 0
        assert "Starting to create a badge" in result.output
        assert "pushed commit" in result.output
        assert "Endpoint Badge:" in result.output

    @patch("setup_badge.cli.get_repo")
    @patch("setup_badge.cli.checkout_branch")
    @patch("setup_badge.cli.create_badge_dict")
    @patch("setup_badge.cli.create_badge_json")
    @patch("setup_badge.cli.check_badge_changes")
    def test_cli_no_changes_to_push(self, mock_changes, mock_json, mock_dict, mock_checkout, mock_repo):
        mock_repo_inst = MagicMock()
        mock_repo_inst.active_branch.name = "main"
        mock_repo.return_value = mock_repo_inst
        mock_checkout.return_value = True
        mock_dict.return_value = {"schemaVersion": 1}
        mock_json.return_value = True
        mock_changes.return_value = False
        result = self.runner.invoke(main, ["--badge-name", "test-badge"])
        assert result.exit_code == 0
        assert "found no changes" in result.output

    @patch("setup_badge.cli.get_repo")
    @patch("setup_badge.cli.checkout_branch")
    def test_cli_checkout_failure(self, mock_checkout, mock_repo):
        mock_repo.return_value = MagicMock()
        mock_checkout.return_value = False
        result = self.runner.invoke(main, ["--badge-name", "test-badge"])
        assert result.exit_code == 1

    @patch("setup_badge.cli.get_repo")
    @patch("setup_badge.cli.checkout_branch")
    @patch("setup_badge.cli.create_badge_dict")
    @patch("setup_badge.cli.create_badge_json")
    @patch("setup_badge.cli.check_badge_changes")
    @patch("setup_badge.cli.push_changes")
    def test_cli_push_failure(self, mock_push, mock_changes, mock_json, mock_dict, mock_checkout, mock_repo):
        mock_repo_inst = MagicMock()
        mock_repo_inst.active_branch.name = "main"
        mock_repo.return_value = mock_repo_inst
        mock_checkout.return_value = True
        mock_dict.return_value = {"schemaVersion": 1}
        mock_json.return_value = True
        mock_changes.return_value = True
        mock_push.return_value = None
        result = self.runner.invoke(main, ["--badge-name", "test-badge"])
        assert result.exit_code == 1
        assert "failed to push changes to origin" in result.output


class TestCheckoutBranch:
    """Tests for the checkout_branch function covering all 5 scenarios."""

    def test_scenario_a_commit_hash_branch(self, mock_repo):
        """Scenario A: Branch name is a commit hash."""
        # repo.commit should succeed - branch_name IS a commit hash
        mock_repo.commit = MagicMock()
        mock_repo.head.commit = MagicMock(hexsha="def456")
        mock_repo.remote.return_value.push = MagicMock()
        mock_branch = MagicMock()
        mock_branch.checkout.return_value = mock_branch
        mock_repo.create_head = MagicMock(return_value=mock_branch)

        result = checkout_branch(mock_repo, "abc123")

        assert result is not None

    def test_scenario_a_not_commit_hash(self, mock_repo):
        """Scenario A: Branch name is NOT a commit hash (test except block)."""
        # repo.commit should raise BadName - branch_name is NOT a commit hash
        mock_repo.commit = MagicMock(side_effect=git.BadName("Not a commit hash"))
        mock_branch = MagicMock()
        mock_branch.checkout.return_value = mock_branch
        mock_repo.create_head = MagicMock(return_value=mock_branch)

        result = checkout_branch(mock_repo, "not-a-commit-hash")

        # Should fall through to scenario B (branch doesn't exist)
        assert result is not None

    def test_scenario_b_branch_does_not_exist(self, mock_repo):
        """Scenario B: Branch doesn't exist on local or remote."""
        mock_repo.heads = {}
        mock_repo.remote.return_value.refs = []
        mock_branch = MagicMock()
        mock_branch.checkout.return_value = mock_branch
        mock_repo.create_head = MagicMock(return_value=mock_branch)
        mock_repo.remote.return_value.push = MagicMock()

        result = checkout_branch(mock_repo, "new-branch")

        assert result is not None

    def test_scenario_c_branch_only_on_remote(self, mock_repo):
        """Scenario C: Branch exists on remote but not local."""
        import git

        mock_repo.heads = {}
        remote_ref = MagicMock()
        remote_ref.name = "origin/remote-branch"
        mock_repo.remote.return_value.refs = [remote_ref]
        mock_branch = MagicMock()
        mock_branch.checkout.return_value = mock_branch
        mock_repo.create_head = MagicMock(return_value=mock_branch)
        mock_repo.commit = MagicMock(side_effect=git.BadName("Not a commit"))

        result = checkout_branch(mock_repo, "remote-branch")

        assert result is not None

    def test_scenario_d_branch_on_both(self, mock_repo):
        """Scenario D: Branch exists on both local and remote."""
        local_branch = MagicMock()
        local_branch.checkout = MagicMock(return_value=local_branch)
        mock_repo.heads = {"both-branch": local_branch}
        remote_ref = MagicMock()
        remote_ref.name = "origin/both-branch"
        mock_repo.remote.return_value.refs = [remote_ref]
        mock_repo.git.pull = MagicMock()

        result = checkout_branch(mock_repo, "both-branch")

        assert result is not None

    def test_scenario_e_branch_only_on_local(self, mock_repo):
        """Scenario E: Branch exists on local but not remote."""
        local_branch = MagicMock()
        local_branch.name = "local-only"
        local_branch.tracking_branch = MagicMock(return_value=None)
        local_branch.checkout = MagicMock(return_value=local_branch)
        mock_repo.heads = {"local-only": local_branch}
        mock_repo.remote.return_value.refs = []
        mock_repo.remote.return_value.push = MagicMock()

        result = checkout_branch(mock_repo, "local-only")

        assert result is not None

    def test_git_config_set_when_missing(self, mock_repo):
        """Test that git config is set when missing."""
        reader = MagicMock()
        reader.get_value.side_effect = [None, None]
        mock_repo.config_reader = MagicMock(return_value=reader)
        writer = MagicMock()
        # Make config_writer return a context manager
        writer.__enter__ = MagicMock(return_value=writer)
        writer.__exit__ = MagicMock(return_value=False)
        mock_repo.config_writer = MagicMock(return_value=writer)
        mock_repo.heads = {}
        mock_repo.remote.return_value.refs = []
        mock_branch = MagicMock()
        mock_branch.checkout.return_value = mock_branch
        mock_repo.create_head = MagicMock(return_value=mock_branch)
        mock_repo.remote.return_value.push = MagicMock()

        checkout_branch(mock_repo, "new-branch")

        # Verify config was set
        assert writer.set_value.call_count >= 2

    def test_exception_on_config_failure(self, mock_repo):
        """Test that an exception is raised when git config fails."""
        reader = MagicMock()
        reader.get_value.side_effect = [None, None]
        mock_repo.config_reader = MagicMock(return_value=reader)
        mock_repo.config_writer = MagicMock(side_effect=Exception("Git config error"))
        mock_repo.heads = {}
        mock_repo.remote.return_value.refs = []

        with pytest.raises(Exception, match="Failed to set git configuration"):
            checkout_branch(mock_repo, "new-branch")

    def test_git_config_with_no_config_file_error(self, mock_repo):
        """Test that git config is set when config_reader raises NoConfigFileError."""
        # configparser.NoConfigFileError doesn't exist; the error is NoSectionError
        # For testing purposes, we just test with a generic exception
        writer = MagicMock()
        writer.__enter__ = MagicMock(return_value=writer)
        writer.__exit__ = MagicMock(return_value=False)
        mock_repo.config_reader = MagicMock(side_effect=Exception("No section: 'user'"))
        mock_repo.config_writer = MagicMock(return_value=writer)
        mock_repo.heads = {}
        mock_repo.remote.return_value.refs = []
        mock_branch = MagicMock()
        mock_branch.checkout.return_value = mock_branch
        mock_repo.create_head = MagicMock(return_value=mock_branch)
        mock_repo.remote.return_value.push = MagicMock()

        result = checkout_branch(mock_repo, "new-branch")

        assert result is not None
        # Verify config was set
        assert writer.set_value.call_count >= 2

    def test_git_config_with_section_error(self, mock_repo):
        """Test that git config is set when config_reader raises NoSectionError."""
        writer = MagicMock()
        writer.__enter__ = MagicMock(return_value=writer)
        writer.__exit__ = MagicMock(return_value=False)
        mock_repo.config_reader = MagicMock(side_effect=Exception("No section: 'user'"))
        mock_repo.config_writer = MagicMock(return_value=writer)
        mock_repo.heads = {}
        mock_repo.remote.return_value.refs = []
        mock_branch = MagicMock()
        mock_branch.checkout.return_value = mock_branch
        mock_repo.create_head = MagicMock(return_value=mock_branch)
        mock_repo.remote.return_value.push = MagicMock()

        result = checkout_branch(mock_repo, "new-branch")

        assert result is not None
        # Verify config was set
        assert writer.set_value.call_count >= 2


class TestCreateShieldsioEndpointBadge:
    def test_endpoint_badge_without_url(self, mock_repo):
        """Test endpoint badge generation without clickable URL."""
        mock_repo.remotes.origin.url = "https://github.com/owner/repo.git"
        badge = create_shieldsio_endpoint_badge(mock_repo, "badges", "test-badge", "")
        assert "![test-badge](https://img.shields.io/endpoint?url=" in badge

    def test_endpoint_badge_with_url(self, mock_repo):
        """Test endpoint badge generation with clickable URL."""
        mock_repo.remotes.origin.url = "https://github.com/owner/repo.git"
        badge = create_shieldsio_endpoint_badge(mock_repo, "badges", "test-badge", "https://example.com")
        assert "[![test-badge](https://img.shields.io/endpoint?url=" in badge
        assert "](https://example.com)" in badge

    def test_endpoint_badge_ssh_url_format(self, mock_repo):
        """Test endpoint badge with SSH URL format."""
        mock_repo.remotes.origin.url = "git@github.com:owner/repo.git"
        badge = create_shieldsio_endpoint_badge(mock_repo, "badges", "test-badge", "")
        assert "![test-badge](https://img.shields.io/endpoint?url=" in badge
        assert "https://raw.githubusercontent.com/owner/repo/" in badge


class TestPushChanges:
    def test_push_changes_success(self, mock_repo):
        """Test successful push of changes."""
        commit = MagicMock()
        commit.hexsha = "abc123def456"
        mock_repo.index.add = MagicMock()
        mock_repo.index.write = MagicMock()
        mock_repo.index.commit = MagicMock(return_value=commit)
        mock_repo.git.push = MagicMock(return_value="")

        result = push_changes(mock_repo, "origin", "badges", "test-badge")

        assert result == "abc123def456"
        mock_repo.index.add.assert_called_once()
        mock_repo.index.commit.assert_called_once()

    def test_push_changes_failure(self, mock_repo):
        """Test push changes when git operation fails."""
        mock_repo.index.add = MagicMock(side_effect=git.BadName("Git push failed"))
        mock_repo.index.write = MagicMock()
        mock_repo.index.commit = MagicMock()

        result = push_changes(mock_repo, "origin", "badges", "test-badge")

        assert result is None


class TestMainFunction:
    def setup_method(self):
        self.runner = CliRunner()

    def test_main_invalid_create_badge_json(self, mock_repo):
        """Test main when create_badge_json returns False."""
        with patch("setup_badge.cli.get_repo", return_value=mock_repo):
            with patch("setup_badge.cli.checkout_branch", return_value=True):
                with patch("setup_badge.cli.create_badge_dict", return_value={"schemaVersion": 1}):
                    with patch("setup_badge.cli.create_badge_json", return_value=False):
                        result = self.runner.invoke(main, ["--badge-name", "test-badge"])
                        assert result.exit_code == 1
                        assert "failed to create test-badge.json" in result.output

    def test_main_checkout_branch_failure(self, mock_repo):
        """Test main when checkout_branch returns False."""
        with patch("setup_badge.cli.get_repo", return_value=mock_repo):
            with patch("setup_badge.cli.checkout_branch", return_value=False):
                result = self.runner.invoke(main, ["--badge-name", "test-badge"])
                assert result.exit_code == 1

    def test_main_exception_handling(self, mock_repo):
        """Test main exception handling."""
        with patch("setup_badge.cli.get_repo", side_effect=Exception("Test error")):
            result = self.runner.invoke(main, ["--badge-name", "test-badge"])
            assert result.exit_code == 1
            assert result.exception is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
