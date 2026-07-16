import math
import unittest
from types import MappingProxyType

from atlas.platform.context_compilation.canonical_json import (
    MAX_SAFE_INTEGER,
    MIN_SAFE_INTEGER,
    InvalidMappingKeyError,
    InvalidUnicodeError,
    UnsafeIntegerError,
    UnsupportedTypeError,
    canonicalize,
    canonicalize_text,
)
from atlas.platform.context_compilation.models import deep_freeze


class CanonicalJSONTests(unittest.TestCase):
    def test_scalars_lists_and_nested_mappings(self) -> None:
        value = {"z": [None, False, True, -1, 0, 1], "a": {"b": "text", "a": []}}
        self.assertEqual(
            canonicalize_text(value),
            '{"a":{"a":[],"b":"text"},"z":[null,false,true,-1,0,1]}',
        )

    def test_booleans_are_not_serialized_as_integers(self) -> None:
        self.assertEqual(canonicalize(True), b"true")
        self.assertEqual(canonicalize(False), b"false")

    def test_safe_integer_boundaries(self) -> None:
        self.assertEqual(canonicalize(MIN_SAFE_INTEGER), str(MIN_SAFE_INTEGER).encode())
        self.assertEqual(canonicalize(MAX_SAFE_INTEGER), str(MAX_SAFE_INTEGER).encode())
        for value in (MIN_SAFE_INTEGER - 1, MAX_SAFE_INTEGER + 1):
            with self.subTest(value=value), self.assertRaises(UnsafeIntegerError):
                canonicalize(value)

    def test_all_floats_are_rejected(self) -> None:
        for value in (0.0, 1.0, -2.5, math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaises(UnsupportedTypeError):
                canonicalize(value)

    def test_non_string_mapping_keys_are_rejected(self) -> None:
        with self.assertRaises(InvalidMappingKeyError):
            canonicalize({1: "one"})
        with self.assertRaises(InvalidMappingKeyError):
            canonicalize({True: "boolean"})

    def test_unsupported_containers_and_types_are_rejected(self) -> None:
        for value in ({1, 2}, frozenset((1, 2)), object()):
            with self.subTest(value=type(value).__name__), self.assertRaises(UnsupportedTypeError):
                canonicalize(value)

    def test_deeply_frozen_values_canonicalize_like_raw_values(self) -> None:
        raw = {"z": [3, {"b": True, "a": None}], "a": "e\u0301"}
        frozen = deep_freeze(raw)
        self.assertIsInstance(frozen, MappingProxyType)
        self.assertIsInstance(frozen["z"], tuple)
        self.assertIsInstance(frozen["z"][1], MappingProxyType)
        self.assertEqual(canonicalize(frozen), canonicalize(raw))
        self.assertEqual(canonicalize(frozen), canonicalize(frozen))

    def test_rfc8785_string_escaping(self) -> None:
        value = "\x00\b\t\n\f\r\x1f\"\\/"
        self.assertEqual(
            canonicalize_text(value),
            '"\\u0000\\b\\t\\n\\f\\r\\u001f\\\"\\\\/"',
        )

    def test_output_is_utf8_without_bom(self) -> None:
        output = canonicalize("€😀")
        self.assertEqual(output, '"€😀"'.encode("utf-8"))
        self.assertFalse(output.startswith(b"\xef\xbb\xbf"))

    def test_unicode_is_not_normalized(self) -> None:
        composed = canonicalize("é")
        decomposed = canonicalize("e\u0301")
        self.assertNotEqual(composed, decomposed)
        self.assertEqual(decomposed, b'"e\xcc\x81"')

    def test_invalid_surrogates_are_rejected_in_values_and_keys(self) -> None:
        for value in ("\ud800", "\udfff", "ok\ud800"):
            with self.subTest(value=repr(value)), self.assertRaises(InvalidUnicodeError):
                canonicalize(value)
        with self.assertRaises(InvalidUnicodeError):
            canonicalize({"\ud800": "value"})

    def test_rfc8785_utf16_property_order_vector(self) -> None:
        value = {
            "€": "Euro Sign",
            "\r": "Carriage Return",
            "דּ": "Hebrew Letter Dalet With Dagesh",
            "1": "One",
            "😀": "Emoji: Grinning Face",
            "\x80": "Control",
            "ö": "Latin Small Letter O With Diaeresis",
        }
        self.assertEqual(
            canonicalize_text(value),
            '{"\\r":"Carriage Return","1":"One","\x80":"Control",'
            '"ö":"Latin Small Letter O With Diaeresis","€":"Euro Sign",'
            '"😀":"Emoji: Grinning Face","דּ":"Hebrew Letter Dalet With Dagesh"}',
        )

    def test_repeat_output_is_byte_identical(self) -> None:
        value = {"nested": [{"b": 2, "a": 1}], "text": "unchanged"}
        first = canonicalize(value)
        for _ in range(20):
            self.assertEqual(canonicalize(value), first)


if __name__ == "__main__":
    unittest.main()
