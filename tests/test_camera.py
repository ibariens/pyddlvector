from __future__ import annotations

from io import BytesIO
from types import SimpleNamespace

from PIL import Image

from pyddlvector.camera import CameraFrame, extract_camera_frame


def test_extract_camera_frame_returns_jpeg_frame() -> None:
    response = SimpleNamespace(
        image_encoding=7,
        frame_time_stamp=123,
        image_id=42,
        data=b"\xff\xd8\xff",
    )

    frame = extract_camera_frame(response)

    assert isinstance(frame, CameraFrame)
    assert frame.timestamp == 123
    assert frame.image_id == 42
    assert frame.data == b"\xff\xd8\xff"


def test_camera_frame_can_be_decoded_and_resized_with_pillow() -> None:
    encoded = BytesIO()
    Image.new("RGB", (16, 8), (200, 100, 50)).save(encoded, format="JPEG")
    frame = extract_camera_frame(SimpleNamespace(image_encoding=7, data=encoded.getvalue()))

    assert frame is not None
    with Image.open(BytesIO(frame.data)) as image:
        assert image.format == "JPEG"
        assert image.size == (16, 8)
        preview = image.convert("RGB").resize((8, 4), Image.Resampling.LANCZOS)
        pixel = preview.getpixel((0, 0))
        assert all(
            abs(actual - expected) <= 2
            for actual, expected in zip(pixel, (200, 100, 50), strict=True)
        )


def test_extract_camera_frame_rejects_non_jpeg() -> None:
    response = SimpleNamespace(
        image_encoding=1,
        frame_time_stamp=1,
        image_id=1,
        data=b"\x00",
    )

    assert extract_camera_frame(response) is None
