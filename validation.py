"""Input validation utilities for PSPlot.

Provides validation functions for user inputs, file paths, and data integrity.
"""

import os
from pathlib import Path
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class FileValidationError(ValidationError):
    """Raised when file path validation fails."""
    pass


def validate_signal_name(name: str) -> str:
    """Validate and sanitize a signal name.
    
    Args:
        name: Raw signal name
        
    Returns:
        Sanitized signal name
        
    Raises:
        ValidationError: If name is invalid
    """
    if not isinstance(name, str):
        raise ValidationError(f"Signal name must be string, got {type(name).__name__}")
    
    name = name.strip()
    if not name:
        raise ValidationError("Signal name cannot be empty")
    
    # Disallow special characters that could cause issues
    forbidden = ['<', '>', ':', '"', '|', '?', '*']
    for char in forbidden:
        if char in name:
            raise ValidationError(f"Signal name cannot contain '{char}'")
    
    return name


def validate_file_path(
    path: str,
    must_exist: bool = True,
    allowed_extensions: Optional[Tuple[str, ...]] = None
) -> Path:
    """Validate a file path.
    
    Args:
        path: File path to validate
        must_exist: Whether file must already exist
        allowed_extensions: Tuple of allowed extensions including dot (e.g., '.txt', '.csv')
        
    Returns:
        Validated Path object
        
    Raises:
        FileValidationError: If path is invalid
    """
    if not isinstance(path, str):
        raise FileValidationError(f"Path must be string, got {type(path).__name__}")
    
    path = path.strip()
    if not path:
        raise FileValidationError("Path cannot be empty")
    
    try:
        p = Path(path).resolve()
    except (OSError, ValueError) as e:
        raise FileValidationError(f"Invalid path format: {e}")
    
    if must_exist and not p.exists():
        raise FileValidationError(f"File does not exist: {p}")
    
    if allowed_extensions:
        ext = p.suffix.lower()
        if ext not in allowed_extensions:
            raise FileValidationError(
                f"Invalid file type '{ext}'. Allowed: {', '.join(allowed_extensions)}"
            )
    
    return p


def validate_export_path(path: str) -> Path:
    """Validate an export file path.
    
    Ensures the directory exists and the path is writable.
    
    Args:
        path: Export file path
        
    Returns:
        Validated Path object
    """
    if not isinstance(path, str):
        raise FileValidationError(f"Path must be string, got {type(path).__name__}")
    
    try:
        p = Path(path).resolve()
    except (OSError, ValueError) as e:
        raise FileValidationError(f"Invalid path: {e}")
    
    # Ensure parent directory exists
    if not p.parent.exists():
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {p.parent}")
        except OSError as e:
            raise FileValidationError(f"Cannot create directory {p.parent}: {e}")
    
    # Check if directory is writable
    if not os.access(p.parent, os.W_OK):
        raise FileValidationError(f"Directory is not writable: {p.parent}")
    
    return p


def validate_subplot_count(count: int, max_count: int = 6) -> int:
    """Validate subplot count.
    
    Args:
        count: Requested subplot count
        max_count: Maximum allowed subplots
        
    Returns:
        Validated count
        
    Raises:
        ValidationError: If count is invalid
    """
    if not isinstance(count, int):
        try:
            count = int(count)
        except (TypeError, ValueError):
            raise ValidationError(f"Subplot count must be integer, got {type(count).__name__}")
    
    if count < 1:
        raise ValidationError(f"Subplot count must be at least 1, got {count}")
    
    if count > max_count:
        raise ValidationError(f"Subplot count cannot exceed {max_count}, got {count}")
    
    return count


def validate_margins(
    left: float,
    right: float,
    top: float,
    bottom: float
) -> Tuple[float, float, float, float]:
    """Validate plot margins.
    
    Args:
        left: Left margin (0-1)
        right: Right margin (0-1)
        top: Top margin (0-1)
        bottom: Bottom margin (0-1)
        
    Returns:
        Validated margin tuple
        
    Raises:
        ValidationError: If margins are invalid
    """
    margins = {'left': left, 'right': right, 'top': top, 'bottom': bottom}
    
    for name, value in margins.items():
        if not isinstance(value, (int, float)):
            raise ValidationError(f"{name} margin must be numeric, got {type(value).__name__}")
        
        if not 0 <= value <= 1:
            raise ValidationError(f"{name} margin must be between 0 and 1, got {value}")
    
    if left >= right:
        raise ValidationError(f"Left margin ({left}) must be less than right ({right})")
    
    if bottom >= top:
        raise ValidationError(f"Bottom margin ({bottom}) must be less than top ({top})")
    
    return (left, right, top, bottom)


def validate_color(color: str) -> str:
    """Validate matplotlib color string.
    
    Supports:
        - Named colors (e.g., 'red', 'blue', 'green')
        - Hex colors (e.g., '#FF0000', '#00f')
        - RGB tuples (e.g., '(1, 0, 0)', '(1,0,0)')
        
    Args:
        color: Color string to validate
        
    Returns:
        Normalized color string
        
    Raises:
        ValidationError: If color is invalid
    """
    if not isinstance(color, str):
        raise ValidationError(f"Color must be string, got {type(color).__name__}")
    
    color = color.strip()
    
    # Check for hex color
    if color.startswith('#'):
        hex_part = color[1:]
        if len(hex_part) not in (3, 6):
            raise ValidationError(f"Invalid hex color: {color}")
        try:
            int(hex_part, 16)
            return color.lower()
        except ValueError:
            raise ValidationError(f"Invalid hex color: {color}")
    
    # Check for RGB tuple
    if color.startswith('(') and color.endswith(')'):
        # Accept and return as-is for matplotlib
        return color
    
    # Named color - matplotlib will validate later
    valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
    if not all(c in valid_chars for c in color):
        raise ValidationError(f"Invalid color name characters: {color}")
    
    return color


def sanitize_filename(name: str, default: str = "untitled") -> str:
    """Sanitize a filename for safe use on disk.
    
    Args:
        name: Raw filename
        default: Default name if sanitized result is empty
        
    Returns:
        Safe filename
    """
    if not isinstance(name, str):
        name = str(name)
    
    # Remove forbidden characters
    forbidden_chars = '<>:"/\\|?*'
    for char in forbidden_chars:
        name = name.replace(char, '_')
    
    # Remove control characters
    name = ''.join(char for char in name if ord(char) >= 32)
    
    # Remove leading/trailing dots and spaces
    name = name.strip('. ')
    
    # Use default if empty
    if not name:
        name = default
    
    return name
