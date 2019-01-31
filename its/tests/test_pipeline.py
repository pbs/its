import itertools
import os
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from PIL import Image

import its.errors
from its.application import APP
from its.optimize import optimize
from its.pipeline import process_transforms


def get_pixels(image):
    # List of all the possible coordinates in the image
    coords = list(itertools.product(range(image.width), range(image.height)))
    # list of all pixels in the image
    pixels = [image.getpixel(coord) for coord in coords]

    return pixels


def compare_pixels(img1, img2, tolerance=0):
    def pixel_matches(pixel1, pixel2, tolerance):
        matching_vals = [abs(pixel1[i] - pixel2[i]) <= tolerance for i in range(3)]
        return all(matching_vals)

    img1_pixels = get_pixels(img1)
    img2_pixels = get_pixels(img2)
    matches = 0
    total = len(img1_pixels)  # both images should have the same number of pixels

    for pixel_pair in zip(img1_pixels, img2_pixels):
        if pixel_matches(pixel_pair[0], pixel_pair[1], tolerance):
            matches += 1

    return matches / total


class TestFitTransform(TestCase):
    @classmethod
    def setUpClass(self):
        self.img_dir = Path(__file__).parent / "images"

    @patch("its.transformations.fit.FitTransform.apply_transform")
    def test_default_fit_no_alpha(self, MockFitTransform):
        fit_transform = MockFitTransform()
        test_image = Image.open(self.img_dir / "middle.png")
        test_image.info["filename"] = "middle.png"
        query = {"fit": "100x100"}
        fit_transform.return_value = True
        fit_transform(test_image, query)
        fit_transform.assert_called_with(test_image, query)

    @patch("its.transformations.fit.FitTransform.apply_transform")
    def test_default_crop_no_alpha(self, MockFitTransform):
        fit_transform = MockFitTransform()
        test_image = Image.open(self.img_dir / "middle.png")
        test_image.info["filename"] = "middle.png"
        query = {"crop": "100x100"}
        fit_transform.return_value = True
        fit_transform(test_image, query)
        fit_transform.assert_called_with(test_image, query)

    @patch("its.transformations.fit.FitTransform.apply_transform")
    def test_focal_fit_no_alpha(self, MockFitTransform):
        fit_transform = MockFitTransform()
        test_image = Image.open(self.img_dir / "top_left.png")
        test_image.info["filename"] = "top_left.png"
        query = {"fit": "1x1x1x1"}
        fit_transform.return_value = True
        fit_transform(test_image, query)
        fit_transform.assert_called_with(test_image, query)

    @patch("its.transformations.fit.FitTransform.apply_transform")
    def test_focal_crop_no_alpha(self, MockFitTransform):
        fit_transform = MockFitTransform()
        test_image = Image.open(self.img_dir / "top_left.png")
        test_image.info["filename"] = "top_left.png"
        query = {"crop": "1x1x1x1"}
        fit_transform.return_value = True
        fit_transform(test_image, query)
        fit_transform.assert_called_with(test_image, query)

    @patch("its.transformations.fit.FitTransform.apply_transform")
    def test_focal_1x1_no_alpha(self, MockFitTransform):
        fit_transform = MockFitTransform()
        test_image = Image.open(self.img_dir / "abstract.png")
        test_image.info["filename"] = "abstract.png"
        query = {"fit": "28x34x1x1"}
        fit_transform.return_value = True
        fit_transform(test_image, query)
        fit_transform.assert_called_with(test_image, query)

    @patch("its.transformations.fit.FitTransform.apply_transform")
    def test_focalcrop_1x1_no_alpha(self, MockFitTransform):
        fit_transform = MockFitTransform()
        test_image = Image.open(self.img_dir / "abstract.png")
        test_image.info["filename"] = "abstract.png"
        query = {"crop": "28x34x1x1"}
        fit_transform.return_value = True
        fit_transform(test_image, query)
        fit_transform.assert_called_with(test_image, query)

    @patch("its.transformations.fit.FitTransform.apply_transform")
    def test_focal_100x100_no_alpha(self, MockFitTransform):
        fit_transform = MockFitTransform()
        test_image = Image.open(self.img_dir / "abstract.png")
        test_image.info["filename"] = "abstract.png"
        query = {"fit": "1x1x100x100"}
        fit_transform.return_value = True
        fit_transform(test_image, query)
        fit_transform.assert_called_with(test_image, query)

    @patch("its.transformations.fit.FitTransform.apply_transform")
    def test_focalcrop_100x100_no_alpha(self, MockFitTransform):
        fit_transform = MockFitTransform()
        test_image = Image.open(self.img_dir / "abstract.png")
        test_image.info["filename"] = "abstract.png"
        query = {"crop": "1x1x100x100"}
        fit_transform.return_value = True
        fit_transform(test_image, query)
        fit_transform.assert_called_with(test_image, query)

    @patch("its.transformations.fit.FitTransform.apply_transform")
    def test_smart_70x1_no_alpha(self, MockFitTransform):
        fit_transform = MockFitTransform()
        test_image = Image.open(self.img_dir / "abstract_focus-70x1.png")
        test_image.info["filename"] = "abstract_focus-70x1.png"
        query = {"fit": "5x100"}
        fit_transform.return_value = True
        fit_transform(test_image, query)
        fit_transform.assert_called_with(test_image, query)

    @patch("its.transformations.fit.FitTransform.apply_transform")
    def test_smartcrop_70x1_no_alpha(self, MockFitTransform):
        fit_transform = MockFitTransform()
        test_image = Image.open(self.img_dir / "abstract_focus-70x1.png")
        test_image.info["filename"] = "abstract_focus-70x1.png"
        query = {"crop": "5x100"}
        fit_transform.return_value = True
        fit_transform(test_image, query)
        fit_transform.assert_called_with(test_image, query)

    def test_invalid_fit_size(self):
        test_image = Image.open(self.img_dir / "test.png")
        test_image.info["filename"] = "test.png"
        query = {"fit": "5x0"}

        with self.assertRaises(its.errors.ITSClientError):
            process_transforms(test_image, query)

    def test_invalid_crop_size(self):
        test_image = Image.open(self.img_dir / "test.png")
        test_image.info["filename"] = "test.png"
        query = {"crop": "5x0"}

        with self.assertRaises(its.errors.ITSClientError):
            process_transforms(test_image, query)

    def test_invalid_focal_percentages(self):
        test_image = Image.open(self.img_dir / "test.png")
        test_image.info["filename"] = "test.png"
        query = {"fit": "100x100x150x150"}

        with self.assertRaises(its.errors.ITSClientError):
            process_transforms(test_image, query)

    def test_invalid_crop_focal_percentages(self):
        test_image = Image.open(self.img_dir / "test.png")
        test_image.info["filename"] = "test.png"
        query = {"crop": "100x100x150x150"}

        with self.assertRaises(its.errors.ITSClientError):
            process_transforms(test_image, query)


class TestResizeTransform(TestCase):
    @classmethod
    def setUpClass(self):
        # current directory / images
        self.img_dir = Path(__file__).parent / "images"
        self.threshold = 0.5

    def test_resize_size(self):
        test_image = Image.open(self.img_dir / "abstract.png")
        test_image.info["filename"] = "abstract.png"
        query = {"resize": "10x10"}
        result = process_transforms(test_image, query)
        self.assertEqual(result.size, (10, 10))

    def test_resize_without_height(self):
        test_image = Image.open(self.img_dir / "abe.jpg")
        test_image.info["filename"] = "abe.jpg"
        query = {"resize": "100x"}
        result = process_transforms(test_image, query)
        self.assertEqual(result.width, 100)
        self.assertEqual(result.height, 131)

    def test_resize_without_width(self):
        test_image = Image.open(self.img_dir / "abe.jpg")
        test_image.info["filename"] = "abe.jpg"
        query = {"resize": "x100"}
        result = process_transforms(test_image, query)
        self.assertEqual(result.width, 76)
        self.assertEqual(result.height, 100)

    def test_resize_integrity_smaller(self):
        test_image = Image.open(self.img_dir / "test.png")
        test_image.info["filename"] = "test.png"
        query = {"resize": "100x100"}
        expected = Image.open(self.img_dir / "expected/test_resize.png")
        actual = process_transforms(test_image, query)
        # can't use norm since resizing can cause noise
        comparison = compare_pixels(expected, actual)
        self.assertGreaterEqual(comparison, self.threshold)

    def test_resize_integrity_larger(self):
        test_image = Image.open(self.img_dir / "test.png")
        test_image.info["filename"] = "test.png"
        query = {"resize": "700x550"}
        expected = Image.open(self.img_dir / "expected/test_resize_700x550.png")
        actual = process_transforms(test_image, query)
        comparison = compare_pixels(expected, actual)
        self.assertGreaterEqual(comparison, self.threshold)

    def test_invalid_resize(self):
        test_image = Image.open(self.img_dir / "test.png")
        query = {"resize": "100"}

        with self.assertRaises(its.errors.ITSClientError):
            process_transforms(test_image, query)

    def test_resize_format(self):
        test_image = Image.open(self.img_dir / "test.png")
        query = {"resize": "100x100", "format": "foo"}

        with self.assertRaises(its.errors.ITSClientError):
            result = process_transforms(test_image, query)
            optimize(result, query)


class TestImageResults(TestCase):
    @classmethod
    def setUpClass(self):
        # current directory / images
        self.img_dir = Path(__file__).parent / "images"

    def test_jpg_progressive(self):
        test_image = Image.open(self.img_dir / "middle.png")
        result = optimize(test_image, {"format": "jpg"})
        self.assertEqual(result.info["progressive"], 1)

    def test_jpg_quality_vs_size(self):
        test_image = Image.open(self.img_dir / "middle.png")
        quality_1 = optimize(test_image, {"quality": 1, "format": "jpg"})
        with tempfile.NamedTemporaryFile(dir=".", delete=True) as tmp_file_1:
            quality_1.save(tmp_file_1.name, format=quality_1.format)
            q1_size = os.stat(tmp_file_1.name).st_size

        quality_10 = optimize(test_image, {"quality": 10, "format": "jpg"})
        with tempfile.NamedTemporaryFile(dir=".", delete=True) as tmp_file_2:
            quality_10.save(tmp_file_2.name, format=quality_10.format)
            q10_size = os.stat(tmp_file_2.name).st_size

        self.assertLessEqual(q1_size, q10_size)

    def test_png_quality_vs_size(self):
        test_image = Image.open(self.img_dir / "test.png")
        quality_1 = optimize(test_image, {"quality": "1"})
        with tempfile.NamedTemporaryFile(dir=".", delete=True) as tmp_file_1:
            quality_1.save(tmp_file_1.name, format=quality_1.format)
            q1_size = os.stat(tmp_file_1.name).st_size

        quality_10 = optimize(test_image, {"quality": "10"})
        with tempfile.NamedTemporaryFile(dir=".", delete=True) as tmp_file_2:
            quality_10.save(tmp_file_2.name, format=quality_10.format)
            q10_size = os.stat(tmp_file_2.name).st_size

        self.assertLessEqual(q1_size, q10_size)


class TestPipelineEndToEnd(TestCase):
    @classmethod
    def setUpClass(self):
        APP.config["TESTING"] = True
        self.client = APP.test_client()
        self.img_dir = Path(__file__).parent / "images"
        self.threshold = 0.99

    def test_secret_png(self):
        response = self.client.get("tests/images/secretly-a-png.jpg.resize.800x450.jpg")
        assert response.status_code == 200

    def test_cmyk_jpg_to_rgb_png(self):
        response = self.client.get("/tests/images/cmyk.jpg.resize.380x190.png")
        assert response.status_code == 200

    def test_svg_passthrough(self):
        reference_image = BytesIO(
            open(self.img_dir / "wikipedia_logo.svg", "rb").read()
        )
        response = self.client.get(
            "/tests/images/wikipedia_logo.svg?fit=10x10&format=png&resize=500x500"
        )
        assert response.status_code == 200
        assert response.mimetype == "image/svg+xml"
        assert response.data == reference_image.getvalue()

    def test_grayscale_png_to_jpg(self):
        response = self.client.get("tests/images/grayscale.png.fit.2048x876.jpg")
        assert response.status_code == 200
        assert response.mimetype == "image/jpeg"

    def test_jpg_to_webp(self):
        response = self.client.get("tests/images/seagull.jpg?format=webp")
        assert response.status_code == 200
        assert response.mimetype == "image/webp"

    def test_jpg_without_extension_to_png(self):
        response = self.client.get("tests/images/seagull.resize.900x500.png")
        assert response.status_code == 200
        assert response.mimetype == "image/png"

    def test_jpg_without_extension_to_focalcrop(self):
        response = self.client.get("tests/images/seagull.focalcrop.312x464.50.50.png")
        assert response.status_code == 200
        assert response.mimetype == "image/png"

    def test_focal_crop_without_filename_priority(self):
        # case 1: resize and crop with query parameters
        ref_img_500_500_50_10 = Image.open(
            "{}/expected/seagull-500-500-50-10.jpg".format(self.img_dir)
        )
        response = self.client.get("/tests/images/seagull.jpg?fit=500x500x50x10")
        assert response.status_code == 200
        assert response.mimetype == "image/jpeg"
        comparison = compare_pixels(
            ref_img_500_500_50_10, Image.open(BytesIO(response.data)), tolerance=10
        )
        self.assertGreaterEqual(comparison, 0.95)

    def test_focal_crop_filename_priority(self):
        # case 2: resize and crop with query parameters and filename focus: filename focus wins
        ref_img_500_500_10_90 = Image.open(
            "{}/expected/seagull-500-500-10-90.jpg".format(self.img_dir)
        )
        response = self.client.get(
            "/tests/images/seagull_focus-10x90.jpg?fit=500x500x50x10"
        )
        assert response.status_code == 200
        assert response.mimetype == "image/jpeg"
        comparison = compare_pixels(
            ref_img_500_500_10_90, Image.open(BytesIO(response.data)), tolerance=10
        )
        self.assertGreaterEqual(comparison, 0.95)

    def test_small_vertical_resize(self):
        response = self.client.get("tests/images/vertical-line.png.resize.710x399.png")
        assert response.status_code == 200
        assert response.mimetype == "image/png"

    def test_auto_format_flat_jpeg(self):
        response = self.client.get("tests/images/test.jpeg?format=auto")
        assert response.status_code == 200
        assert response.mimetype == "image/png"

    def test_cache_control_on_200(self):
        response = self.client.get("tests/images/test.jpeg?format=auto")
        assert response.status_code == 200
        assert response.mimetype == "image/png"
        assert response.headers["Cache-Control"] == "max-age=31536000"

    def test_auto_format_complex_jpeg(self):
        response = self.client.get("tests/images/seagull?format=auto")
        assert response.status_code == 200
        assert response.mimetype == "image/jpeg"

    def test_focalcrop_parity(self):
        old_style_response = self.client.get(
            "tests/images/test.png.focalcrop.767x421.50.10.png"
        )
        new_style_response = self.client.get(
            "tests/images/test.png?focalcrop=767x421x50x10&format=png"
        )
        comparison = compare_pixels(
            Image.open(BytesIO(old_style_response.data)),
            Image.open(BytesIO(new_style_response.data)),
        )
        self.assertGreaterEqual(comparison, self.threshold)

    def test_resize_without_height(self):
        response = self.client.get("tests/images/seagull?resize=80x&format=png")
        assert response.status_code == 200
        assert response.mimetype == "image/png"

    def test_valid_blur_request(self):
        response = self.client.get("tests/images/test.jpeg?blur=100")
        assert response.status_code == 200

    def test_blur_zero_value_parity(self):
        old_style_response = self.client.get("tests/images/test.png")
        new_style_response = self.client.get("tests/images/test.png?blur=0")
        comparison = compare_pixels(
            Image.open(BytesIO(old_style_response.data)),
            Image.open(BytesIO(new_style_response.data)),
        )

        self.assertEqual(comparison, 1)

    def test_blur_non_parity(self):
        old_style_response = self.client.get("tests/images/test.png")
        new_style_response = self.client.get("tests/images/test.png?blur=1")
        comparison = compare_pixels(
            Image.open(BytesIO(old_style_response.data)),
            Image.open(BytesIO(new_style_response.data)),
        )
        self.assertLessEqual(comparison, self.threshold)

    def test_invalid_blur_request_alpha_value(self):
        response = self.client.get("tests/images/test.jpeg?blur=a")
        assert response.status_code == 400

    def test_invalid_blur_request_no_value(self):
        response = self.client.get("tests/images/test.jpeg?blur=")
        assert response.status_code == 400


if __name__ == "__main__":
    unittest.main()
