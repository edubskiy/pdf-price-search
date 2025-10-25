"""
Unit tests for PDFLoaderService.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from src.application.services.pdf_loader_service import PDFLoaderService
from src.application.exceptions import PDFLoadException
from src.application.config import AppConfig
from src.infrastructure.pdf.repository import PriceRepositoryInterface


@pytest.fixture
def mock_repository():
    """Create a mock repository."""
    repo = Mock(spec=PriceRepositoryInterface)
    repo.load_from_pdf = Mock(return_value=[Mock()])  # Returns list of services
    return repo


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = Mock(spec=AppConfig)
    config.default_pdf_directory = "/default/pdf/dir"
    config.max_pdf_size_mb = 10
    return config


@pytest.fixture
def loader_service(mock_repository, mock_config):
    """Create a PDF loader service instance."""
    return PDFLoaderService(mock_repository, mock_config)


class TestPDFLoaderServiceInitialization:
    """Test PDFLoaderService initialization."""

    def test_create_loader_service(self, mock_repository, mock_config):
        """Test creating a PDF loader service."""
        loader = PDFLoaderService(mock_repository, mock_config)
        assert loader.repository == mock_repository
        assert loader.config == mock_config
        assert loader.get_loaded_pdfs() == []
        assert loader.get_loaded_count() == 0


class TestLoadSinglePDF:
    """Test loading a single PDF file."""

    def test_load_valid_pdf(self, loader_service, mock_repository):
        """Test loading a valid PDF file."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name
            f.write(b"fake pdf content")

        try:
            loader_service.load_pdf(pdf_path)
            assert pdf_path in loader_service.get_loaded_pdfs()
            assert loader_service.get_loaded_count() == 1
            mock_repository.load_from_pdf.assert_called_once_with(pdf_path)
        finally:
            os.unlink(pdf_path)

    def test_load_nonexistent_pdf_raises_error(self, loader_service):
        """Test that loading non-existent PDF raises PDFLoadException."""
        with pytest.raises(PDFLoadException) as exc_info:
            loader_service.load_pdf("/nonexistent/file.pdf")
        assert "does not exist" in str(exc_info.value).lower()

    def test_load_directory_as_pdf_raises_error(self, loader_service):
        """Test that loading a directory as PDF raises PDFLoadException."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(PDFLoadException) as exc_info:
                loader_service.load_pdf(tmpdir)
            assert "not a file" in str(exc_info.value).lower()

    def test_load_non_pdf_file_raises_error(self, loader_service):
        """Test that loading non-PDF file raises PDFLoadException."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            txt_path = f.name
            f.write(b"not a pdf")

        try:
            with pytest.raises(PDFLoadException) as exc_info:
                loader_service.load_pdf(txt_path)
            assert "not a pdf" in str(exc_info.value).lower()
        finally:
            os.unlink(txt_path)

    def test_load_pdf_exceeding_size_limit_raises_error(self, loader_service):
        """Test that loading PDF exceeding size limit raises error."""
        # Create a large file (larger than 10MB limit)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name
            # Write 11MB of data
            f.write(b"0" * (11 * 1024 * 1024))

        try:
            with pytest.raises(PDFLoadException) as exc_info:
                loader_service.load_pdf(pdf_path)
            assert "exceeds maximum" in str(exc_info.value).lower()
        finally:
            os.unlink(pdf_path)

    def test_load_pdf_with_repository_error(self, loader_service, mock_repository):
        """Test handling repository errors during PDF load."""
        mock_repository.load_from_pdf.side_effect = Exception("Parse error")

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name
            f.write(b"fake pdf content")

        try:
            with pytest.raises(PDFLoadException) as exc_info:
                loader_service.load_pdf(pdf_path)
            assert "failed to parse" in str(exc_info.value).lower()
        finally:
            os.unlink(pdf_path)


class TestLoadPDFsFromDirectory:
    """Test loading PDFs from a directory."""

    def test_load_pdfs_from_directory_with_multiple_pdfs(self, loader_service, mock_repository):
        """Test loading multiple PDFs from a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple PDF files
            pdf_files = []
            for i in range(3):
                pdf_path = os.path.join(tmpdir, f"test{i}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(b"fake pdf content")
                pdf_files.append(pdf_path)

            count = loader_service.load_pdfs_from_directory(tmpdir)
            assert count == 3
            assert loader_service.get_loaded_count() == 3

    def test_load_pdfs_from_nonexistent_directory_raises_error(self, loader_service):
        """Test that loading from non-existent directory raises error."""
        with pytest.raises(PDFLoadException) as exc_info:
            loader_service.load_pdfs_from_directory("/nonexistent/directory")
        assert "does not exist" in str(exc_info.value).lower()

    def test_load_pdfs_from_file_instead_of_directory_raises_error(self, loader_service):
        """Test that loading from file instead of directory raises error."""
        with tempfile.NamedTemporaryFile() as f:
            with pytest.raises(PDFLoadException) as exc_info:
                loader_service.load_pdfs_from_directory(f.name)
            assert "not a directory" in str(exc_info.value).lower()

    def test_load_pdfs_from_empty_directory(self, loader_service):
        """Test loading PDFs from empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            count = loader_service.load_pdfs_from_directory(tmpdir)
            assert count == 0

    def test_load_pdfs_from_directory_with_non_pdf_files(self, loader_service):
        """Test loading from directory with only non-PDF files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create non-PDF files
            for i in range(3):
                path = os.path.join(tmpdir, f"test{i}.txt")
                with open(path, "w") as f:
                    f.write("not a pdf")

            count = loader_service.load_pdfs_from_directory(tmpdir)
            assert count == 0

    def test_load_pdfs_partial_success(self, loader_service, mock_repository):
        """Test partial success when some PDFs load and some fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple PDF files
            good_pdf = os.path.join(tmpdir, "good.pdf")
            with open(good_pdf, "wb") as f:
                f.write(b"fake pdf content")

            bad_pdf = os.path.join(tmpdir, "bad.pdf")
            with open(bad_pdf, "wb") as f:
                f.write(b"fake pdf content")

            # Mock repository to fail on bad.pdf
            def load_side_effect(path):
                if "bad" in path:
                    raise Exception("Parse error")
                return [Mock()]

            mock_repository.load_from_pdf.side_effect = load_side_effect

            count = loader_service.load_pdfs_from_directory(tmpdir)
            assert count == 1  # Only good.pdf should load

    def test_load_pdfs_all_fail_raises_exception(self, loader_service, mock_repository):
        """Test that exception is raised when all PDFs fail to load."""
        mock_repository.load_from_pdf.side_effect = Exception("Parse error")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create PDF files
            for i in range(2):
                path = os.path.join(tmpdir, f"test{i}.pdf")
                with open(path, "wb") as f:
                    f.write(b"fake pdf content")

            with pytest.raises(PDFLoadException) as exc_info:
                loader_service.load_pdfs_from_directory(tmpdir)
            assert "all pdf loads failed" in str(exc_info.value).lower()


class TestLoadDefaultPDFs:
    """Test loading default PDFs."""

    def test_load_default_pdfs_success(self, loader_service, mock_repository, mock_config):
        """Test successfully loading default PDFs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mock_config.default_pdf_directory = tmpdir

            # Create a PDF file
            pdf_path = os.path.join(tmpdir, "test.pdf")
            with open(pdf_path, "wb") as f:
                f.write(b"fake pdf content")

            loader_service.load_default_pdfs()
            assert loader_service.get_loaded_count() == 1

    def test_load_default_pdfs_directory_not_exists(self, loader_service, mock_config):
        """Test loading default PDFs when directory doesn't exist."""
        mock_config.default_pdf_directory = "/nonexistent/directory"

        with pytest.raises(PDFLoadException):
            loader_service.load_default_pdfs()


class TestValidatePDF:
    """Test PDF validation."""

    def test_validate_valid_pdf(self, loader_service):
        """Test validating a valid PDF file."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name
            f.write(b"fake pdf content")

        try:
            assert loader_service.validate_pdf(pdf_path) is True
        finally:
            os.unlink(pdf_path)

    def test_validate_nonexistent_pdf(self, loader_service):
        """Test validating non-existent PDF."""
        assert loader_service.validate_pdf("/nonexistent/file.pdf") is False

    def test_validate_directory_as_pdf(self, loader_service):
        """Test validating directory instead of PDF."""
        with tempfile.TemporaryDirectory() as tmpdir:
            assert loader_service.validate_pdf(tmpdir) is False

    def test_validate_non_pdf_file(self, loader_service):
        """Test validating non-PDF file."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            txt_path = f.name
            f.write(b"not a pdf")

        try:
            assert loader_service.validate_pdf(txt_path) is False
        finally:
            os.unlink(txt_path)

    def test_validate_pdf_exceeding_size_limit(self, loader_service, mock_config):
        """Test validating PDF exceeding size limit."""
        # Set a very small limit
        mock_config.max_pdf_size_mb = 0.001  # 1KB

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            pdf_path = f.name
            # Write 2KB of data
            f.write(b"0" * 2048)

        try:
            assert loader_service.validate_pdf(pdf_path) is False
        finally:
            os.unlink(pdf_path)


class TestClearLoadedPDFs:
    """Test clearing loaded PDFs."""

    def test_clear_loaded_pdfs(self, loader_service, mock_repository):
        """Test clearing the list of loaded PDFs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Load a PDF
            pdf_path = os.path.join(tmpdir, "test.pdf")
            with open(pdf_path, "wb") as f:
                f.write(b"fake pdf content")

            loader_service.load_pdf(pdf_path)
            assert loader_service.get_loaded_count() == 1

            # Clear
            loader_service.clear_loaded_pdfs()
            assert loader_service.get_loaded_count() == 0
            assert loader_service.get_loaded_pdfs() == []


class TestGetLoadedPDFs:
    """Test getting loaded PDFs."""

    def test_get_loaded_pdfs_returns_copy(self, loader_service, mock_repository):
        """Test that get_loaded_pdfs returns a copy, not the original list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = os.path.join(tmpdir, "test.pdf")
            with open(pdf_path, "wb") as f:
                f.write(b"fake pdf content")

            loader_service.load_pdf(pdf_path)

            loaded_pdfs = loader_service.get_loaded_pdfs()
            loaded_pdfs.append("fake_path")

            # Original list should not be affected
            assert len(loader_service.get_loaded_pdfs()) == 1

    def test_get_loaded_count(self, loader_service, mock_repository):
        """Test getting the count of loaded PDFs."""
        assert loader_service.get_loaded_count() == 0

        with tempfile.TemporaryDirectory() as tmpdir:
            # Load multiple PDFs
            for i in range(3):
                pdf_path = os.path.join(tmpdir, f"test{i}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(b"fake pdf content")
                loader_service.load_pdf(pdf_path)

            assert loader_service.get_loaded_count() == 3
