"""Tests for input validation utilities."""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from psplot.core.validation import (
    ValidationError,
    FileValidationError,
    validate_signal_name,
    validate_file_path,
    validate_export_path,
    validate_subplot_count,
    validate_margins,
    validate_color,
    sanitize_filename,
)


class TestValidateSignalName:
    """Tests for validate_signal_name function."""
    
    def test_valid_names(self):
        """Test that valid signal names are returned unchanged."""
        assert validate_signal_name("Voltage_1") == "Voltage_1"
        assert validate_signal_name("Current-A") == "Current-A"
        assert validate_signal_name("  Trimmed  ") == "Trimmed"
    
    def test_empty_name_raises(self):
        """Test that empty strings raise ValidationError."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_signal_name("")
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_signal_name("   ")
    
    def test_non_string_raises(self):
        """Test that non-string values raise ValidationError."""
        with pytest.raises(ValidationError, match="must be string"):
            validate_signal_name(123)
        with pytest.raises(ValidationError, match="must be string"):
            validate_signal_name(None)
    
    def test_forbidden_characters(self):
        """Test that forbidden characters raise ValidationError."""
        forbidden = ['<', '>', ':', '"', '|', '?', '*']
        for char in forbidden:
            with pytest.raises(ValidationError, match=f"cannot contain '{char}'"):
                validate_signal_name(f"signal{char}name")


class TestValidateFilePath:
    """Tests for validate_file_path function."""
    
    def test_valid_existing_file(self, tmp_path):
        """Test that existing files are returned as Path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        result = validate_file_path(str(test_file))
        assert isinstance(result, Path)
        assert result.exists()
    
    def test_must_exist_false(self, tmp_path):
        """Test that non-existent files are accepted when must_exist=False."""
        test_file = tmp_path / "nonexistent.txt"
        
        result = validate_file_path(str(test_file), must_exist=False)
        assert isinstance(result, Path)
        assert not result.exists()
    
    def test_must_exist_true_raises(self, tmp_path):
        """Test that non-existent files raise when must_exist=True."""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(FileValidationError, match="does not exist"):
            validate_file_path(str(test_file), must_exist=True)
    
    def test_allowed_extensions(self, tmp_path):
        """Test that file extensions are validated."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content")
        
        # Should pass with .txt extension
        validate_file_path(str(txt_file), allowed_extensions=('.txt', '.csv'))
        
        # Should fail with wrong extension
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("content")
        
        with pytest.raises(FileValidationError, match="Invalid file type"):
            validate_file_path(str(csv_file), allowed_extensions=('.txt',))
    
    def test_empty_path_raises(self):
        """Test that empty paths raise FileValidationError."""
        with pytest.raises(FileValidationError, match="cannot be empty"):
            validate_file_path("")
        with pytest.raises(FileValidationError, match="cannot be empty"):
            validate_file_path("   ")
    
    def test_non_string_raises(self):
        """Test that non-string paths raise FileValidationError."""
        with pytest.raises(FileValidationError, match="must be string"):
            validate_file_path(123)
    
    def test_invalid_path_format(self):
        """Test that invalid path formats raise FileValidationError."""
        with pytest.raises(FileValidationError, match="Invalid path format"):
            validate_file_path("\x00invalid")


class TestValidateExportPath:
    """Tests for validate_export_path function."""
    
    def test_creates_parent_directory(self, tmp_path):
        """Test that parent directories are created if needed."""
        nested_dir = tmp_path / "nested" / "deep"
        export_path = nested_dir / "output.png"
        
        assert not nested_dir.exists()
        result = validate_export_path(str(export_path))
        
        assert nested_dir.exists()
        assert isinstance(result, Path)
    
    def test_validates_writable(self, tmp_path):
        """Test that writable directories are validated."""
        # This test works on Unix systems where we can chmod
        if os.name == 'posix':
            readonly_dir = tmp_path / "readonly"
            readonly_dir.mkdir()
            os.chmod(readonly_dir, 0o555)  # Remove write permission
            
            try:
                with pytest.raises(FileValidationError, match="not writable"):
                    validate_export_path(str(readonly_dir / "file.txt"))
            finally:
                os.chmod(readonly_dir, 0o755)  # Restore permissions
    
    def test_non_string_raises(self):
        """Test that non-string paths raise FileValidationError."""
        with pytest.raises(FileValidationError, match="must be string"):
            validate_export_path(123)


class TestValidateSubplotCount:
    """Tests for validate_subplot_count function."""
    
    def test_valid_counts(self):
        """Test valid subplot counts are returned."""
        assert validate_subplot_count(1) == 1
        assert validate_subplot_count(3) == 3
        assert validate_subplot_count(6) == 6
    
    def test_string_numbers(self):
        """Test that string numbers are converted."""
        assert validate_subplot_count("4") == 4
    
    def test_zero_raises(self):
        """Test that zero raises ValidationError."""
        with pytest.raises(ValidationError, match="at least 1"):
            validate_subplot_count(0)
    
    def test_negative_raises(self):
        """Test that negative numbers raise ValidationError."""
        with pytest.raises(ValidationError, match="at least 1"):
            validate_subplot_count(-1)
    
    def test_exceeds_max_raises(self):
        """Test that counts exceeding max raise ValidationError."""
        with pytest.raises(ValidationError, match="cannot exceed"):
            validate_subplot_count(7)
    
    def test_non_numeric_raises(self):
        """Test that non-numeric values raise ValidationError."""
        with pytest.raises(ValidationError, match="must be integer"):
            validate_subplot_count("abc")
    
    def test_custom_max(self):
        """Test that custom max_count is respected."""
        assert validate_subplot_count(10, max_count=10) == 10
        with pytest.raises(ValidationError, match="cannot exceed"):
            validate_subplot_count(11, max_count=10)


class TestValidateMargins:
    """Tests for validate_margins function."""
    
    def test_valid_margins(self):
        """Test that valid margins are returned as tuple."""
        result = validate_margins(0.1, 0.9, 0.9, 0.1)
        assert result == (0.1, 0.9, 0.9, 0.1)
    
    def test_left_greater_than_right_raises(self):
        """Test that left >= right raises ValidationError."""
        with pytest.raises(ValidationError, match="Left margin"):
            validate_margins(0.6, 0.5, 0.9, 0.1)
    
    def test_bottom_greater_than_top_raises(self):
        """Test that bottom >= top raises ValidationError."""
        with pytest.raises(ValidationError, match="Bottom margin"):
            validate_margins(0.1, 0.9, 0.2, 0.3)
    
    def test_out_of_range_raises(self):
        """Test that margins outside 0-1 raise ValidationError."""
        with pytest.raises(ValidationError, match="between 0 and 1"):
            validate_margins(-0.1, 0.9, 0.9, 0.1)
        
        with pytest.raises(ValidationError, match="between 0 and 1"):
            validate_margins(0.1, 1.1, 0.9, 0.1)
    
    def test_non_numeric_raises(self):
        """Test that non-numeric margins raise ValidationError."""
        with pytest.raises(ValidationError, match="must be numeric"):
            validate_margins("0.1", 0.9, 0.9, 0.1)


class TestValidateColor:
    """Tests for validate_color function."""
    
    def test_valid_hex_colors(self):
        """Test that hex colors are validated and lowercased."""
        assert validate_color("#FF0000") == "#ff0000"
        assert validate_color("#00f") == "#00f"
        assert validate_color("#aabbcc") == "#aabbcc"
    
    def test_invalid_hex_raises(self):
        """Test that invalid hex colors raise ValidationError."""
        with pytest.raises(ValidationError, match="Invalid hex color"):
            validate_color("#FF00")  # 4 chars
        with pytest.raises(ValidationError, match="Invalid hex color"):
            validate_color("#GHI")  # Non-hex chars
    
    def test_valid_named_colors(self):
        """Test that named colors pass validation."""
        assert validate_color("red") == "red"
        assert validate_color("blue") == "blue"
        assert validate_color("darkgreen") == "darkgreen"
    
    def test_rgb_tuples(self):
        """Test that RGB tuples are accepted."""
        assert validate_color("(1, 0, 0)") == "(1, 0, 0)"
        assert validate_color("(0.5,0.5,0.5)") == "(0.5,0.5,0.5)"
    
    def test_invalid_named_characters(self):
        """Test that named colors with invalid chars raise."""
        with pytest.raises(ValidationError, match="Invalid color name"):
            validate_color("red<")
    
    def test_non_string_raises(self):
        """Test that non-string colors raise ValidationError."""
        with pytest.raises(ValidationError, match="must be string"):
            validate_color(123)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""
    
    def test_valid_filenames(self):
        """Test that valid filenames are unchanged."""
        assert sanitize_filename("signal.png") == "signal.png"
        assert sanitize_filename("data_2024.csv") == "data_2024.csv"
    
    def test_replaces_forbidden_chars(self):
        """Test that forbidden characters are replaced."""
        assert sanitize_filename("a<b") == "a_b"
        assert sanitize_filename("a>b") == "a_b"
        assert sanitize_filename("a:b") == "a_b"
        assert sanitize_filename('a"b') == 'a_b'
        assert sanitize_filename("a/b") == "a_b"
        assert sanitize_filename("a\\b") == "a_b"
        assert sanitize_filename("a|b") == "a_b"
        assert sanitize_filename("a?b") == "a_b"
        assert sanitize_filename("a*b") == "a_b"
    
    def test_strips_leading_dots_spaces(self):
        """Test that leading/trailing dots and spaces are stripped."""
        assert sanitize_filename("  file.txt  ") == "file.txt"
        assert sanitize_filename("...file.txt...") == "file.txt"
    
    def test_removes_control_chars(self):
        """Test that control characters are removed."""
        assert sanitize_filename("file\x00\x01\x02.txt") == "file.txt"
    
    def test_default_name_for_empty(self):
        """Test that empty result uses default name."""
        assert sanitize_filename("", default="backup") == "backup"
        assert sanitize_filename("...", default="backup") == "backup"
    
    def test_default_parameter(self):
        """Test that default parameter works."""
        assert sanitize_filename("", default="custom_default") == "custom_default"
    
    def test_converts_non_string(self):
        """Test that non-strings are converted to strings."""
        assert sanitize_filename(123) == "123"
