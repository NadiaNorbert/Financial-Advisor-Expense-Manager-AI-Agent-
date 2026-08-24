# OCR sub-package
"""OCR sub-package – image-to-expense extraction."""
from backend.ocr.expense_ocr import extract_expense_from_image

__all__ = ["extract_expense_from_image"]