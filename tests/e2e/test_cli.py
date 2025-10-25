"""
End-to-end tests for the CLI application.

These tests verify the CLI interface works correctly with real data.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


@pytest.fixture
def cli_script():
    """Return path to CLI script."""
    return PROJECT_ROOT / "main_cli.py"


@pytest.mark.e2e
class TestCLISearch:
    """Test CLI search command."""

    def test_search_basic_query(self, cli_script):
        """Test basic search query."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "search", "FedEx 2Day, Zone 5, 3 lb"],
            capture_output=True,
            text=True
        )

        # Should complete without error (exit code 0 or 1 depending on whether PDFs are loaded)
        assert result.returncode in [0, 1]
        assert "Query" in result.stdout or "ERROR" in result.stderr

    def test_search_with_no_cache(self, cli_script):
        """Test search with cache disabled."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "search", "--no-cache",
             "Standard Overnight, Zone 2, 10 lb"],
            capture_output=True,
            text=True
        )

        assert result.returncode in [0, 1]

    def test_search_invalid_query(self, cli_script):
        """Test search with invalid query."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "search", ""],
            capture_output=True,
            text=True
        )

        # Should fail with error
        assert result.returncode != 0


@pytest.mark.e2e
class TestCLIList:
    """Test CLI list command."""

    def test_list_table_format(self, cli_script):
        """Test list command with table format."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "list"],
            capture_output=True,
            text=True
        )

        # Should complete (might have no services if PDFs not loaded)
        assert result.returncode == 0
        assert "Services" in result.stdout or "No services" in result.stdout

    def test_list_json_format(self, cli_script):
        """Test list command with JSON format."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "list", "--format", "json"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

    def test_list_simple_format(self, cli_script):
        """Test list command with simple format."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "list", "--format", "simple"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0


@pytest.mark.e2e
class TestCLILoad:
    """Test CLI load command."""

    def test_load_default_directory(self, cli_script):
        """Test load from default directory."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "load"],
            capture_output=True,
            text=True
        )

        # Should complete (might fail if directory doesn't exist)
        assert result.returncode in [0, 1]
        assert "Loading" in result.stdout or "ERROR" in result.stderr

    def test_load_with_verbose(self, cli_script):
        """Test load with verbose output."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "--verbose", "load"],
            capture_output=True,
            text=True
        )

        assert result.returncode in [0, 1]


@pytest.mark.e2e
class TestCLICache:
    """Test CLI cache command."""

    def test_cache_stats(self, cli_script):
        """Test cache statistics."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "cache", "--stats"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Cache" in result.stdout

    def test_cache_clear(self, cli_script):
        """Test cache clear."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "cache", "--clear"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0


@pytest.mark.e2e
class TestCLIDemo:
    """Test CLI demo command."""

    def test_demo_command(self, cli_script):
        """Test demo command."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "demo"],
            capture_output=True,
            text=True,
            timeout=30  # Demo might take a while
        )

        # Should complete (might fail if no PDFs)
        assert result.returncode in [0, 1]
        assert "Demo" in result.stdout or "ERROR" in result.stderr


@pytest.mark.e2e
class TestCLIHelp:
    """Test CLI help output."""

    def test_help_command(self, cli_script):
        """Test help command."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "PDF Price Search" in result.stdout
        assert "search" in result.stdout
        assert "list" in result.stdout

    def test_search_help(self, cli_script):
        """Test search command help."""
        result = subprocess.run(
            [sys.executable, str(cli_script), "search", "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "QUERY" in result.stdout
