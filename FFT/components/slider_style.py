"""Slider stylesheet."""

# slider_style.py

slider_style = """
    QSlider::groove:horizontal {
        border: 1px solid #999999;
        background: #e0e0e0;
        height: 8px;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background: #3c3a9e;
        border: 1px solid #5c5c5c;
        width: 20px;
        height: 20px;
        border-radius: 10px;
    }

    QSlider::sub-page:horizontal {
        background: #3c3a9e;
        border-radius: 4px;
    }
    QSlider::add-page:horizontal {
        background: #e0e0e0;
        border-radius: 4px;
    }
"""


def apply_slider_style(slider):
    """Apply the stylesheet in the slider object."""
    slider.setStyleSheet(slider_style)
    slider.setMinimumHeight(
        30
    )  # Optional: Increase the height of the slider for better visibility
