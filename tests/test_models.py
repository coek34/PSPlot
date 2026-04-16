"""Tests for data models."""

import pytest
import numpy as np
import logging

from models import (
    ValidationError,
    Signal,
    SignalGroup,
    Channel,
    ImportedData,
)


class TestSignal:
    """Tests for Signal dataclass."""
    
    def test_basic_creation(self):
        """Test basic Signal creation with minimal args."""
        signal = Signal(name="Volt_1")
        assert signal.name == "Volt_1"
        assert signal.channel_name == "Unknown"
        assert signal.group_name == "Unknown"
        assert len(signal.x) == 0
        assert len(signal.y) == 0
    
    def test_full_creation(self):
        """Test Signal creation with all arguments."""
        x = np.array([0, 1, 2, 3], dtype=float)
        y = np.array([0, 1, 4, 9], dtype=float)
        
        signal = Signal(
            name="Volt_1",
            channel_name="Bus_A",
            group_name="Voltage",
            x=x,
            y=y,
            color="#FF0000",
            line_style="dashed",
            visible=True,
            label="Output Voltage"
        )
        
        assert signal.name == "Volt_1"
        assert signal.channel_name == "Bus_A"
        assert signal.group_name == "Voltage"
        assert np.array_equal(signal.x, x)
        assert np.array_equal(signal.y, y)
        assert signal.color == "#FF0000"
        assert signal.line_style == "dashed"
        assert signal.visible is True
        assert signal.label == "Output Voltage"
    
    def test_empty_name_raises(self):
        """Test that empty signal name raises ValidationError."""
        with pytest.raises(ValidationError, match="non-empty string"):
            Signal(name="")
    
    def test_none_name_raises(self):
        """Test that None signal name raises ValidationError."""
        with pytest.raises(ValidationError, match="non-empty string"):
            Signal(name=None)
    
    def test_mismatched_arrays_raises(self):
        """Test that mismatched x/y lengths raise ValidationError."""
        with pytest.raises(ValidationError, match="same length"):
            Signal(name="Test", x=np.array([1, 2]), y=np.array([1, 2, 3]))
    
    def test_invalid_line_style_raises(self):
        """Test that invalid line styles raise ValidationError."""
        with pytest.raises(ValidationError, match="Invalid line_style"):
            Signal(name="Test", line_style="invalid_style")
    
    def test_valid_line_styles(self):
        """Test that valid line styles pass."""
        for style in ['solid', 'dashed', 'dotted', 'dashdot', None]:
            signal = Signal(name="Test", line_style=style)
            assert signal.line_style == style
    
    def test_non_string_channel_name_raises(self):
        """Test that non-string channel name raises ValidationError."""
        with pytest.raises(ValidationError, match="Channel name must be a string"):
            Signal(name="Test", channel_name=123)
    
    def test_non_string_group_name_raises(self):
        """Test that non-string group name raises ValidationError."""
        with pytest.raises(ValidationError, match="Group name must be a string"):
            Signal(name="Test", group_name=123)
    
    def test_list_arrays_converted(self):
        """Test that list arrays are converted to numpy."""
        signal = Signal(name="Test", x=[1, 2, 3], y=[4, 5, 6])
        assert isinstance(signal.x, np.ndarray)
        assert isinstance(signal.y, np.ndarray)
        assert np.array_equal(signal.x, np.array([1.0, 2.0, 3.0]))
        assert np.array_equal(signal.y, np.array([4.0, 5.0, 6.0]))
    
    def test_invalid_array_convversion_raises(self):
        """Test that invalid array types raise ValidationError."""
        with pytest.raises(ValidationError, match="Cannot convert x data"):
            Signal(name="Test", x="invalid", y=np.array([1]))
    
    def test_invalid_color_raises(self):
        """Test that non-string colors raise ValidationError."""
        with pytest.raises(ValidationError, match="Color must be a string"):
            Signal(name="Test", color=123)
    
    def test_empty_array_warning(self, caplog):
        """Test that empty arrays trigger warning."""
        with caplog.at_level(logging.WARNING):
            Signal(name="TestSignal", x=np.array([]), y=np.array([]))
            assert "has empty data arrays" in caplog.text
            assert "TestSignal" in caplog.text
    
    def test_display_name(self):
        """Test display_name property."""
        signal_with_label = Signal(name="V1", label="Voltage Output")
        assert signal_with_label.display_name == "Voltage Output"
        
        signal_without_label = Signal(name="V1")
        assert signal_without_label.display_name == "V1"
    
    def test_full_name(self):
        """Test full_name property."""
        signal = Signal(name="V1", channel_name="Bus_A", group_name="Voltage")
        assert signal.full_name == "Bus_A.Voltage.V1"
    
    def test_is_valid(self):
        """Test is_valid method."""
        valid_signal = Signal(name="Test", x=np.array([1, 2]), y=np.array([1, 2]))
        assert valid_signal.is_valid() is True
        
        empty_signal = Signal(name="Test")
        assert empty_signal.is_valid() is False
        
        invisible_signal = Signal(name="Test", x=np.array([1]), y=np.array([1]), visible=False)
        assert invisible_signal.is_valid() is False
    
    def test_to_dict(self):
        """Test to_dict method."""
        signal = Signal(
            name="V1",
            channel_name="Bus_A",
            group_name="Voltage",
            x=np.array([1, 2]),
            y=np.array([3, 4]),
            color="red"
        )
        d = signal.to_dict()
        
        assert d['name'] == "V1"
        assert d['channel_name'] == "Bus_A"
        assert d['group_name'] == "Voltage"
        assert np.array_equal(d['x'], np.array([1, 2]))
        assert np.array_equal(d['y'], np.array([3, 4]))
        assert d['color'] == "red"
    
    def test_from_dict_basic(self):
        """Test from_dict with minimal data."""
        data = {'name': 'V1'}
        signal = Signal.from_dict(data)
        
        assert signal.name == "V1"
        assert signal.channel_name == "Unknown"
        assert signal.group_name == "Unknown"
    
    def test_from_dict_complete(self):
        """Test from_dict with all fields."""
        data = {
            'name': 'V1',
            'channel_name': 'Bus_A',
            'group_name': 'Voltage',
            'x': np.array([1, 2]),
            'y': np.array([3, 4]),
            'color': 'red',
            'line_style': 'solid',
            'visible': False,
            'label': 'Output'
        }
        signal = Signal.from_dict(data)
        
        assert signal.name == "V1"
        assert signal.channel_name == "Bus_A"
        assert signal.group_name == "Voltage"
        assert np.array_equal(signal.x, np.array([1, 2]))
        assert np.array_equal(signal.y, np.array([3, 4]))
        assert signal.color == "red"
        assert signal.line_style == "solid"
        assert signal.visible is False
        assert signal.label == "Output"
    
    def test_from_dict_missing_defaults(self):
        """Test from_dict applies defaults for missing values."""
        data = {}  # Completely empty
        signal = Signal.from_dict(data)
        
        assert signal.name == "Unknown"
        assert signal.channel_name == "Unknown"
        assert signal.group_name == "Unknown"
        assert signal.visible is True
    
    def test_from_dict_invalid_raises(self):
        """Test that from_dict raises ValidationError for invalid data."""
        # This should raise because empty name is invalid
        with pytest.raises(ValidationError):
            Signal.from_dict({'name': ''})
    
    def test_get_xy_range_empty(self):
        """Test get_xy_range for empty signal."""
        signal = Signal(name="Empty")
        assert signal.get_xy_range() == (0.0, 0.0, 0.0, 0.0)
    
    def test_get_xy_range_with_data(self):
        """Test get_xy_range for signal with data."""
        signal = Signal(name="Test", x=np.array([0, 1, 2]), y=np.array([-5, 0, 10]))
        result = signal.get_xy_range()
        
        assert result == (0.0, 2.0, -5.0, 10.0)
    
    def test_get_xy_range_negative_values(self):
        """Test get_xy_range with negative values."""
        signal = Signal(
            name="Test",
            x=np.array([-10, -5, 0]),
            y=np.array([-100, -50, -10])
        )
        result = signal.get_xy_range()
        
        assert result == (-10.0, 0.0, -100.0, -10.0)


class TestSignalGroup:
    """Tests for SignalGroup dataclass."""
    
    def test_basic_creation(self):
        """Test SignalGroup creation."""
        group = SignalGroup(name="Voltage")
        assert group.name == "Voltage"
        assert group.signals == []
        assert group.expanded is True
    
    def test_creation_with_signals(self):
        """Test SignalGroup creation with existing signals."""
        signals = [
            Signal(name="V1"),
            Signal(name="V2"),
        ]
        group = SignalGroup(name="Voltage", signals=signals)
        
        assert len(group.signals) == 2
        assert group.signals[0].name == "V1"
    
    def test_add_signal(self):
        """Test adding signals to group."""
        group = SignalGroup(name="Voltage")
        signal = Signal(name="V1")
        
        group.add_signal(signal)
        
        assert len(group.signals) == 1
        assert group.signals[0].name == "V1"
    
    def test_get_signal_found(self):
        """Test get_signal when signal exists."""
        group = SignalGroup(name="Voltage")
        signal = Signal(name="V1")
        group.add_signal(signal)
        
        result = group.get_signal("V1")
        assert result is not None
        assert result.name == "V1"
    
    def test_get_signal_not_found(self):
        """Test get_signal when signal doesn't exist."""
        group = SignalGroup(name="Voltage")
        group.add_signal(Signal(name="V1"))
        
        result = group.get_signal("NonExistent")
        assert result is None


class TestChannel:
    """Tests for Channel dataclass."""
    
    def test_basic_creation(self):
        """Test basic Channel creation."""
        channel = Channel(name="Bus_A")
        assert channel.name == "Bus_A"
        assert channel.groups == []
        assert channel.expanded is True
    
    def test_add_group(self):
        """Test adding groups to channel."""
        channel = Channel(name="Bus_A")
        group = SignalGroup(name="Voltage")
        
        channel.add_group(group)
        
        assert len(channel.groups) == 1
        assert channel.groups[0].name == "Voltage"
    
    def test_find_signal_found(self):
        """Test find_signal when signal exists in group."""
        channel = Channel(name="Bus_A")
        group = SignalGroup(name="Voltage")
        signal = Signal(name="V1")
        group.add_signal(signal)
        channel.add_group(group)
        
        result = channel.find_signal("V1")
        assert result is not None
        assert result.name == "V1"
    
    def test_find_signal_not_found(self):
        """Test find_signal when signal doesn't exist."""
        channel = Channel(name="Bus_A")
        group = SignalGroup(name="Voltage")
        group.add_signal(Signal(name="V1"))
        channel.add_group(group)
        
        result = channel.find_signal("NonExistent")
        assert result is None
    
    def test_find_signal_across_groups(self):
        """Test find_signal searches all groups."""
        channel = Channel(name="Bus_A")
        
        group1 = SignalGroup(name="Voltage")
        group1.add_signal(Signal(name="V1"))
        
        group2 = SignalGroup(name="Current")
        group2.add_signal(Signal(name="I1"))
        
        channel.add_group(group1)
        channel.add_group(group2)
        
        assert channel.find_signal("V1").name == "V1"
        assert channel.find_signal("I1").name == "I1"
    
    def test_all_signals(self):
        """Test all_signals method."""
        channel = Channel(name="Bus_A")
        
        group1 = SignalGroup(name="Voltage")
        group1.add_signal(Signal(name="V1"))
        group1.add_signal(Signal(name="V2"))
        
        group2 = SignalGroup(name="Current")
        group2.add_signal(Signal(name="I1"))
        
        channel.add_group(group1)
        channel.add_group(group2)
        
        result = channel.all_signals()
        assert len(result) == 3
        names = [s.name for s in result]
        assert "V1" in names
        assert "V2" in names
        assert "I1" in names


class TestImportedData:
    """Tests for ImportedData dataclass."""
    
    def test_basic_creation(self):
        """Test basic ImportedData creation."""
        data = ImportedData()
        assert data.channels == []
    
    def test_add_channel(self):
        """Test adding channels."""
        data = ImportedData()
        channel = Channel(name="Channel1")
        
        data.add_channel(channel)
        
        assert len(data.channels) == 1
        assert data.channels[0].name == "Channel1"
    
    def test_find_signal_across_channels(self):
        """Test find_signal searches all channels."""
        data = ImportedData()
        
        # Channel 1 with signal
        channel1 = Channel(name="Bus_A")
        group1 = SignalGroup(name="Voltage")
        group1.add_signal(Signal(name="V1"))
        channel1.add_group(group1)
        
        # Channel 2 with signal
        channel2 = Channel(name="Bus_B")
        group2 = SignalGroup(name="Current")
        group2.add_signal(Signal(name="I1"))
        channel2.add_group(group2)
        
        data.add_channel(channel1)
        data.add_channel(channel2)
        
        assert data.find_signal("V1").name == "V1"
        assert data.find_signal("I1").name == "I1"
        assert data.find_signal("NonExistent") is None
    
    def test_find_signal_with_group(self):
        """Test find_signal_with_group method."""
        data = ImportedData()
        
        channel = Channel(name="Bus_A")
        group = SignalGroup(name="Voltage")
        group.add_signal(Signal(name="V1"))
        channel.add_group(group)
        data.add_channel(channel)
        
        signal, group_name = data.find_signal_with_group("V1")
        assert signal.name == "V1"
        assert group_name == "Voltage"
        
        signal, group_name = data.find_signal_with_group("NonExistent")
        assert signal is None
        assert group_name is None
    
    def test_all_signals(self):
        """Test all_signals across all channels."""
        data = ImportedData()
        
        # Multiple channels with multiple groups
        channel1 = Channel(name="Bus_A")
        group1 = SignalGroup(name="Voltage")
        group1.add_signal(Signal(name="V1"))
        group1.add_signal(Signal(name="V2"))
        channel1.add_group(group1)
        
        channel2 = Channel(name="Bus_B")
        group2 = SignalGroup(name="Current")
        group2.add_signal(Signal(name="I1"))
        channel2.add_group(group2)
        
        data.add_channel(channel1)
        data.add_channel(channel2)
        
        result = data.all_signals()
        assert len(result) == 3
