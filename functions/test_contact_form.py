"""Unit tests for contact form validation. Run: python test_contact_form.py"""
import unittest

from main import _validate


class TestContactValidation(unittest.TestCase):
    def test_valid_minimal(self):
        self.assertEqual(
            _validate(
                {
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "message": "Ten chars!!",
                    "inquiry_type": "consulting",
                }
            ),
            [],
        )

    def test_invalid_email(self):
        errs = _validate(
            {
                "name": "Jane Doe",
                "email": "not-an-email",
                "message": "Ten chars!!",
                "inquiry_type": "other",
            }
        )
        self.assertTrue(any("email" in e.lower() for e in errs))

    def test_invalid_inquiry_type(self):
        errs = _validate(
            {
                "name": "Jane Doe",
                "email": "j@e.co",
                "message": "Ten chars!!",
                "inquiry_type": "intomeeting",
            }
        )
        self.assertTrue(any("inquiry" in e.lower() for e in errs))


if __name__ == "__main__":
    unittest.main()
