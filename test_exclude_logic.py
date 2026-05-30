"""Regression tests for directory exclusion logic across all entry points.

Verifies that exclusion uses exact directory-name matching, not substring matching.
Covers: FileMasterPro.py, clean_my_folder.py, folder_organizer_pro.py

Run:  python test_exclude_logic.py
      (no third-party dependencies required)
"""
import os
import sys
import shutil
import unittest
from unittest.mock import MagicMock
from types import ModuleType

# ---------------------------------------------------------------------------
# Stub out GUI/optional third-party modules so source files can be imported
# in a clean environment without send2trash, customtkinter, or tkinter.
# ---------------------------------------------------------------------------
_STUBS = {}
for mod_name in (
    "send2trash",
    "customtkinter",
    "tkinter",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.scrolledtext",
):
    if mod_name not in sys.modules:
        stub = ModuleType(mod_name)
        stub.__dict__.setdefault("__all__", [])
        # customtkinter needs CTk, CTkButton, etc. as callables
        stub.__dict__.setdefault("__getattr__", lambda name: MagicMock())
        sys.modules[mod_name] = stub
        _STUBS[mod_name] = stub

# Now safe to import the project modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from FileMasterPro import FileOrganizer, EXCLUDE_FOLDERS as FMP_EXCLUDE
import clean_my_folder
import folder_organizer_pro


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
TEST_TREE_DIR = os.path.join(HERE, "_test_scan_tree")


def _make_organizer():
    """Create a FileOrganizer without GUI."""
    org = FileOrganizer(log_callback=lambda msg: None)
    return org


def _build_scan_tree():
    """Build a directory tree with folders that should/shouldn't be excluded."""
    if os.path.exists(TEST_TREE_DIR):
        shutil.rmtree(TEST_TREE_DIR)
    os.makedirs(TEST_TREE_DIR)

    for name, filename, content in [
        ("normal_folder", "readme.txt", "hello"),
        ("templates", "index.html", "<html></html>"),
        ("temporary", "data.csv", "a,b"),
        ("tmp", "cache.bin", "binary"),
        ("temp", "scratch.dat", "scratch"),
        ("node_modules", "package.json", "{}"),
    ]:
        d = os.path.join(TEST_TREE_DIR, name)
        os.makedirs(d)
        with open(os.path.join(d, filename), "w") as f:
            f.write(content)

    return TEST_TREE_DIR


def _teardown_scan_tree():
    if os.path.exists(TEST_TREE_DIR):
        shutil.rmtree(TEST_TREE_DIR, ignore_errors=True)


# ---------------------------------------------------------------------------
# FileMasterPro.py — FileOrganizer.is_excluded_folder
# ---------------------------------------------------------------------------
class TestFileMasterProExclude(unittest.TestCase):

    def setUp(self):
        self.org = _make_organizer()

    def test_tmp_excluded(self):
        self.assertTrue(self.org.is_excluded_folder("tmp", r"C:\projects\tmp"))

    def test_temp_excluded(self):
        self.assertTrue(self.org.is_excluded_folder("temp", r"C:\work\temp"))

    def test_node_modules_excluded(self):
        self.assertTrue(self.org.is_excluded_folder("node_modules", "/project/node_modules"))

    def test_templates_not_excluded(self):
        self.assertFalse(self.org.is_excluded_folder("templates", r"C:\project\templates"))

    def test_normal_folder_not_excluded(self):
        self.assertFalse(self.org.is_excluded_folder("normal_folder", r"C:\tmp\project\normal_folder"))

    def test_temporary_not_excluded(self):
        self.assertFalse(self.org.is_excluded_folder("temporary", r"C:\work\temporary"))

    def test_user_exclude_custom(self):
        self.assertTrue(self.org.is_excluded_folder("mydata", r"C:\work\mydata", {"mydata"}))


# ---------------------------------------------------------------------------
# FileMasterPro.py — FileOrganizer.is_powerful_excluded_folder
# ---------------------------------------------------------------------------
class TestFileMasterProPowerfulExclude(unittest.TestCase):

    def setUp(self):
        self.org = _make_organizer()

    def test_temp_excluded_case_insensitive(self):
        self.assertTrue(self.org.is_powerful_excluded_folder("Temp", r"C:\Temp"))
        self.assertTrue(self.org.is_powerful_excluded_folder("TEMP", r"C:\TEMP"))

    def test_templates_not_excluded(self):
        self.assertFalse(self.org.is_powerful_excluded_folder("templates", r"C:\templates"))

    def test_temporary_not_excluded(self):
        self.assertFalse(self.org.is_powerful_excluded_folder("temporary", r"D:\temporary"))

    def test_mywindows_not_excluded(self):
        self.assertFalse(self.org.is_powerful_excluded_folder("MyWindows", r"D:\MyWindows"))

    def test_windows_excluded(self):
        self.assertTrue(self.org.is_powerful_excluded_folder("Windows", r"C:\Windows"))


# ---------------------------------------------------------------------------
# clean_my_folder.py — module-level is_excluded_folder
# ---------------------------------------------------------------------------
class TestCleanMyFolderExclude(unittest.TestCase):

    def test_tmp_excluded(self):
        self.assertTrue(clean_my_folder.is_excluded_folder("tmp", r"C:\tmp"))

    def test_temp_excluded(self):
        self.assertTrue(clean_my_folder.is_excluded_folder("temp", r"D:\temp"))

    def test_node_modules_excluded(self):
        self.assertTrue(clean_my_folder.is_excluded_folder("node_modules", "/app/node_modules"))

    def test_templates_not_excluded(self):
        self.assertFalse(clean_my_folder.is_excluded_folder("templates", r"C:\project\templates"))

    def test_normal_folder_not_excluded(self):
        self.assertFalse(clean_my_folder.is_excluded_folder("normal_folder", r"C:\tmp\normal_folder"))

    def test_temporary_not_excluded(self):
        self.assertFalse(clean_my_folder.is_excluded_folder("temporary", r"C:\work\temporary"))


# ---------------------------------------------------------------------------
# folder_organizer_pro.py — module-level is_excluded_folder
# ---------------------------------------------------------------------------
class TestFolderOrganizerProExclude(unittest.TestCase):

    def test_tmp_excluded(self):
        self.assertTrue(folder_organizer_pro.is_excluded_folder("tmp", r"C:\tmp"))

    def test_temp_excluded(self):
        self.assertTrue(folder_organizer_pro.is_excluded_folder("temp", r"D:\temp"))

    def test_node_modules_excluded(self):
        self.assertTrue(folder_organizer_pro.is_excluded_folder("node_modules", "/app/node_modules"))

    def test_templates_not_excluded(self):
        self.assertFalse(folder_organizer_pro.is_excluded_folder("templates", r"C:\project\templates"))

    def test_normal_folder_not_excluded(self):
        self.assertFalse(folder_organizer_pro.is_excluded_folder("normal_folder", r"C:\tmp\normal_folder"))

    def test_temporary_not_excluded(self):
        self.assertFalse(folder_organizer_pro.is_excluded_folder("temporary", r"C:\work\temporary"))


# ---------------------------------------------------------------------------
# Integration: FileOrganizer.scan_files_recursively with real directories
# ---------------------------------------------------------------------------
class TestScanFilesIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tree_root = _build_scan_tree()
        org = _make_organizer()
        files, _, _ = org.scan_files_recursively(cls.tree_root)
        cls.basenames = [os.path.basename(f) for f in files]

    @classmethod
    def tearDownClass(cls):
        _teardown_scan_tree()

    def test_normal_folder_scanned(self):
        self.assertIn("readme.txt", self.basenames)

    def test_templates_scanned(self):
        self.assertIn("index.html", self.basenames)

    def test_temporary_scanned(self):
        self.assertIn("data.csv", self.basenames)

    def test_tmp_skipped(self):
        self.assertNotIn("cache.bin", self.basenames)

    def test_temp_skipped(self):
        self.assertNotIn("scratch.dat", self.basenames)

    def test_node_modules_skipped(self):
        self.assertNotIn("package.json", self.basenames)


# ---------------------------------------------------------------------------
# Integration: clean_my_folder.scan_files_recursively with real directories
# ---------------------------------------------------------------------------
class TestCleanMyFolderScanIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tree_root = _build_scan_tree()
        # Suppress stdout — clean_my_folder prints with emojis that may fail on some codepages
        import io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            files, _, _ = clean_my_folder.scan_files_recursively(cls.tree_root)
        finally:
            sys.stdout = old_stdout
        cls.basenames = [os.path.basename(f) for f in files]

    @classmethod
    def tearDownClass(cls):
        _teardown_scan_tree()

    def test_normal_folder_scanned(self):
        self.assertIn("readme.txt", self.basenames)

    def test_templates_scanned(self):
        self.assertIn("index.html", self.basenames)

    def test_temporary_scanned(self):
        self.assertIn("data.csv", self.basenames)

    def test_tmp_skipped(self):
        self.assertNotIn("cache.bin", self.basenames)

    def test_temp_skipped(self):
        self.assertNotIn("scratch.dat", self.basenames)

    def test_node_modules_skipped(self):
        self.assertNotIn("package.json", self.basenames)


if __name__ == "__main__":
    unittest.main()
