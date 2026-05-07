import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_sidecar import output_binary_name, parse_target_triple


class BuildSidecarTests(unittest.TestCase):
    def test_parse_target_triple_from_rustc_output(self) -> None:
        output = "host: aarch64-apple-darwin\nrelease: 1.95.0\n"
        self.assertEqual(parse_target_triple(output), "aarch64-apple-darwin")

    def test_output_binary_name_for_macos(self) -> None:
        self.assertEqual(
            output_binary_name("kuroneko-studio-bridge", "aarch64-apple-darwin"),
            "kuroneko-studio-bridge-aarch64-apple-darwin",
        )

    def test_output_binary_name_for_windows(self) -> None:
        self.assertEqual(
            output_binary_name("kuroneko-studio-bridge", "x86_64-pc-windows-msvc"),
            "kuroneko-studio-bridge-x86_64-pc-windows-msvc.exe",
        )


if __name__ == "__main__":
    unittest.main()
