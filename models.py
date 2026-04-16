"""Data models for PSPlot - type-safe signal and data structures.

This module provides dataclasses to replace fragile dict-based signal data
and prevent KeyError bugs.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Union
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ValidationError(ValueError):
    """Raised when signal data validation fails."""
    pass


@dataclass
class Signal:
    """Represents a signal with metadata and data arrays.
    
    Replaces dict-based signal data like:
        {'x': [...], 'y': [...], 'name': 'Volt_1', 'channel_name': 'Channel 1', 'group_name': 'Voltage'}
    
    Attributes:
        name: Signal name (e.g., 'Volt_1', 'Current_2')
        channel_name: Channel identifier (e.g., 'Channel 1', 'Bus A')
        group_name: Group within channel (e.g., 'Voltage', 'Exponential')
        x: X-axis data (typically time)
        y: Y-axis data (signal values)
        color: Optional color override (hex color string)
        line_style: Optional line style ('solid', 'dashed', 'dotted', 'dashdot')
        visible: Whether signal should be displayed
        label: Optional custom label for legend (if None, uses name)
    """
    name: str
    channel_name: str = "Unknown"
    group_name: str = "Unknown"
    x: np.ndarray = field(default_factory=lambda: np.array([]))
    y: np.ndarray = field(default_factory=lambda: np.array([]))
    color: Optional[str] = None
    line_style: Optional[str] = None
    visible: bool = True
    label: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate data after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Validate signal data. Raises ValidationError if invalid."""
        # Validate name
        if not self.name or not isinstance(self.name, str):
            raise ValidationError(f"Signal name must be a non-empty string, got: {self.name!r}")
        
        # Validate channel/group names
        if not isinstance(self.channel_name, str):
            raise ValidationError(f"Channel name must be a string, got: {type(self.channel_name)}")
        if not isinstance(self.group_name, str):
            raise ValidationError(f"Group name must be a string, got: {type(self.group_name)}")
        
        # Validate arrays
        if not isinstance(self.x, np.ndarray):
            try:
                object.__setattr__(self, 'x', np.array(self.x, dtype=float))
            except (TypeError, ValueError) as e:
                raise ValidationError(f"Cannot convert x data to numpy array: {e}")
        
        if not isinstance(self.y, np.ndarray):
            try:
                object.__setattr__(self, 'y', np.array(self.y, dtype=float))
            except (TypeError, ValueError) as e:
                raise ValidationError(f"Cannot convert y data to numpy array: {e}")
        
        # Check array lengths
        if len(self.x) != len(self.y):
            raise ValidationError(
                f"Signal '{self.name}': x and y arrays must have same length, "
                f"got x={len(self.x)}, y={len(self.y)}"
            )
        
        # Validate color format if provided
        if self.color is not None and not isinstance(self.color, str):
            raise ValidationError(f"Color must be a string or None, got: {type(self.color)}")
        
        # Validate line_style
        valid_styles = ('solid', 'dashed', 'dotted', 'dashdot', None)
        if self.line_style not in valid_styles:
            raise ValidationError(
                f"Invalid line_style '{self.line_style}'. Must be one of: {valid_styles}"
            )
        
        # Log empty signals
        if len(self.x) == 0:
            logger.warning(f"Signal '{self.name}' has empty data arrays")
    
    @property
    def display_name(self) -> str:
        """Get the display name for legend (custom label or signal name)."""
        return self.label or self.name
    
    @property
    def full_name(self) -> str:
        """Get fully qualified name: channel.group.name"""
        return f"{self.channel_name}.{self.group_name}.{self.name}"
    
    def is_valid(self) -> bool:
        """Check if signal has valid data for plotting."""
        return len(self.x) > 0 and len(self.y) > 0 and self.visible
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility with legacy code."""
        return {
            'name': self.name,
            'channel_name': self.channel_name,
            'group_name': self.group_name,
            'x': self.x,
            'y': self.y,
            'color': self.color,
            'line_style': self.line_style,
            'visible': self.visible,
            'label': self.label,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Signal':
        """Create a Signal from a dictionary (legacy data).
        
        Handles missing keys with defaults and validates the result.
        
        Args:
            data: Dictionary containing signal data
            
        Returns:
            Signal instance
            
        Raises:
            ValidationError: If data is invalid
        """
        try:
            return cls(
                name=data.get('name', 'Unknown'),
                channel_name=data.get('channel_name', 'Unknown'),
                group_name=data.get('group_name', 'Unknown'),
                x=data.get('x', np.array([])),
                y=data.get('y', np.array([])),
                color=data.get('color'),
                line_style=data.get('line_style'),
                visible=data.get('visible', True),
                label=data.get('label'),
            )
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Failed to create Signal from dict: {e}")
    
    def get_xy_range(self) -> Tuple[float, float, float, float]:
        """Get x and y ranges for this signal.
        
        Returns:
            (x_min, x_max, y_min, y_max) or (0, 0, 0, 0) for empty signal
        """
        if len(self.x) == 0 or len(self.y) == 0:
            return (0.0, 0.0, 0.0, 0.0)
        return float(self.x.min()), float(self.x.max()), float(self.y.min()), float(self.y.max())


@dataclass
class SignalGroup:
    """Represents a group of signals within a channel.
    
    Replaces: {'name': 'Voltage', 'signals': [...]}
    """
    name: str
    signals: List[Signal] = field(default_factory=list)
    expanded: bool = True
    
    def add_signal(self, signal: Signal) -> None:
        """Add a signal to this group."""
        self.signals.append(signal)
    
    def get_signal(self, name: str) -> Optional[Signal]:
        """Get a signal by name from this group."""
        for signal in self.signals:
            if signal.name == name:
                return signal
        return None


@dataclass
class Channel:
    """Represents a data channel containing signal groups.
    
    Replaces the nested dict structure from PSCAD import.
    """
    name: str
    groups: List[SignalGroup] = field(default_factory=list)
    expanded: bool = True
    
    def add_group(self, group: SignalGroup) -> None:
        """Add a group to this channel."""
        self.groups.append(group)
    
    def find_signal(self, signal_name: str) -> Optional[Signal]:
        """Find a signal by name across all groups in this channel."""
        for group in self.groups:
            signal = group.get_signal(signal_name)
            if signal:
                return signal
        return None
    
    def all_signals(self) -> List[Signal]:
        """Get all signals from all groups in this channel."""
        return [signal for group in self.groups for signal in group.signals]


@dataclass
class ImportedData:
    """Container for all imported data from a file.
    
    Replaces: list of dicts like [{ 'name': 'Channel 1', 'groups': [...] }]
    """
    channels: List[Channel] = field(default_factory=list)
    
    def add_channel(self, channel: Channel) -> None:
        """Add a channel to this dataset."""
        self.channels.append(channel)
    
    def find_signal(self, signal_name: str) -> Optional[Signal]:
        """Find a signal by name across all channels."""
        for channel in self.channels:
            signal = channel.find_signal(signal_name)
            if signal:
                return signal
        return None
    
    def find_signal_with_group(self, signal_name: str) -> tuple:
        """Find a signal and return (signal, group_name) or (None, None)."""
        for channel in self.channels:
            for group in channel.groups:
                signal = group.get_signal(signal_name)
                if signal:
                    return signal, group.name
        return None, None
    
    def all_signals(self) -> List[Signal]:
        """Get all signals from all channels."""
        return [signal for channel in self.channels for signal in channel.all_signals()]


# Type alias for backward compatibility
SignalData = Signal  # Old name for Signal
