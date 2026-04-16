"""Data models for PSPlot - type-safe signal and data structures.

This module provides dataclasses to replace fragile dict-based signal data
and prevent KeyError bugs.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import numpy as np


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
        color: Optional color override
        line_style: Optional line style (solid, dashed, etc.)
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
    
    def __post_init__(self):
        """Validate data after initialization."""
        if len(self.x) != len(self.y):
            raise ValueError(f"Signal '{self.name}': x and y arrays must have same length")
    
    @property
    def display_name(self) -> str:
        """Get the display name for legend (custom label or signal name)."""
        return self.label or self.name
    
    @property
    def full_name(self) -> str:
        """Get fully qualified name: channel.group.name"""
        return f"{self.channel_name}.{self.group_name}.{self.name}"
    
    def is_valid(self) -> bool:
        """Check if signal has valid data."""
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
        """Create a Signal from a dictionary (legacy data)."""
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
