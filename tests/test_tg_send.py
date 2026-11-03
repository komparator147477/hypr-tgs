import json
import os
from pathlib import Path
import pty
import select
import shlex
import subprocess
import tempfile
import time
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tg-send"


class FileArgumentsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="tg-send-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "telegram.json"
        self.env = os.environ.copy()
        self.env.pop("HYPRLAND_INSTANCE_SIGNATURE", None)
        self.env.update(
            PATH=f"{self.bin}:/usr/bin:/bin",
            TG_TEST_LOG=str(self.log),
        )
        self.stub(
            "Telegram",
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "Path(os.environ['TG_TEST_LOG']).write_text(json.dumps(sys.argv[1:]))\n",
        )

    def stub(self, name, source):
        executable = self.bin / name
        executable.write_text("#!/usr/bin/env python3\n" + source)
        executable.chmod(0o755)

    def files(self, *names):
        paths = []
        for name in names:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            paths.append(str(path))
        return paths

    def run_command(self, *args):
        return subprocess.run(
            [str(SCRIPT), *args], env=self.env, cwd=self.root,
            capture_output=True, text=True, timeout=5,
        )

    def assert_shared(self, result, paths):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.log.read_text()), ["-sendpath", *paths])

    def run_zsh_paste(self, prefix, pasted):
        integration = SCRIPT.with_name("zsh-integration.zsh")
        (self.root / ".zshrc").write_text(
            "PROMPT='TG_READY> '\nRPROMPT=''\nbindkey -e\n"
            f"source {shlex.quote(str(integration))}\n"
            # Reloading the config must not register duplicate hooks.
            f"source {shlex.quote(str(integration))}\n"
        )
        master, slave = pty.openpty()
        env = dict(self.env, ZDOTDIR=str(self.root), TERM="xterm-256color")
        proc = subprocess.Popen(
            ["zsh", "-d", "-i"], stdin=slave, stdout=slave, stderr=slave,
            env=env, cwd=self.root, start_new_session=True,
        )
        os.close(slave)

        def wait_prompt():
            output = b""
            deadline = time.monotonic() + 8
            while b"TG_READY> " not in output:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not select.select([master], [], [], remaining)[0]:
                    self.fail(f"zsh prompt timed out: {output!r}")
                output += os.read(master, 65536)
            return output

        try:
            wait_prompt()
            os.write(master, prefix.encode() + b"\x1b[200~" + pasted.encode() + b"\x1b[201~\r")
            output = wait_prompt().decode(errors="replace")
            self.assertNotIn("permission denied", output)
            self.assertNotIn("no matches found", output)
            self.assertNotIn("command not found", output)
            self.assertNotIn("tg-send:", output)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
            os.close(master)

    def test_separate_arguments(self):
        paths = self.files("first.jpg", "photo (1).jpg", "last.jpg")
        self.assert_shared(self.run_command(*paths), paths)

    def test_yazi_multiline_list(self):
        paths = self.files(
            "20260811_130955.jpg", "20260811_130526.jpg", "20260804_142645.jpg",
            "20260811_115143.jpg", "20260811_115447 (1).jpg", "20260811_115447.jpg",
            "20260811_120804.jpg", "20260811_130455.jpg", "20260811_130501.jpg",
            "20260811_130510.jpg",
        )
        self.assert_shared(self.run_command("\n".join(paths)), paths)

    def test_multiline_preserves_spaces_and_shell_characters(self):
        paths = self.files("folder with spaces/photo (1).jpg", "фото ' [1] $(echo hi).jpg")
        self.assert_shared(self.run_command("\n".join(paths) + "\n"), paths)

    def test_crlf_and_blank_lines(self):
        paths = self.files("first.jpg", "photo (1).jpg")
        self.assert_shared(self.run_command("\r\n" + "\r\n\r\n".join(paths) + "\r\n"), paths)

    def test_legacy_space_split_arguments(self):
        paths = self.files("folder with spaces/first (1).jpg", "last.jpg")
        self.assert_shared(self.run_command(*(" ".join(paths).split(" "))), paths)

    def test_mixed_multiline_and_separate_arguments(self):
        paths = self.files("first.jpg", "second (1).jpg", "last.jpg")
        self.assert_shared(self.run_command("--file", "\n".join(paths[:2]), paths[2]), paths)

    def test_real_filename_with_newline(self):
        paths = self.files("photo\nwith newline.jpg")
        self.assert_shared(self.run_command(*paths), paths)

    def test_missing_file_prevents_launch(self):
        paths = self.files("first.jpg") + [str(self.root / "missing.jpg")]
        result = self.run_command("\n".join(paths))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("file not found:", result.stderr)
        self.assertFalse(self.log.exists())

    def test_empty_list_prevents_launch(self):
        for text in ("", "\n\n", "\r\n"):
            with self.subTest(text=text):
                result = self.run_command(text)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.log.exists())

    def test_interactive_zsh_yazi_paste(self):
        paths = self.files(
            "20260811_130955.jpg", "20260811_130526.jpg", "20260804_142645.jpg",
            "20260811_115143.jpg", "20260811_115447 (1).jpg", "20260811_115447.jpg",
            "20260811_120804.jpg", "20260811_130455.jpg", "20260811_130501.jpg",
            "20260811_130510.jpg",
        )
        self.run_zsh_paste("tg-send ", "\n".join(paths))
        self.assertEqual(json.loads(self.log.read_text()), ["-sendpath", *paths])

    def test_interactive_zsh_single_path_paste(self):
        paths = self.files("folder with spaces/фото ' [1] $(echo hi) (1).jpg")
        self.run_zsh_paste("tg-send ", paths[0])
        self.assertEqual(json.loads(self.log.read_text()), ["-sendpath", *paths])

    def test_interactive_zsh_crlf_paste(self):
        paths = self.files("first.jpg", "photo (1).jpg")
        self.run_zsh_paste("tg-send --file ", "\r\n".join(paths) + "\r\n")
        self.assertEqual(json.loads(self.log.read_text()), ["-sendpath", *paths])

    def test_zsh_hook_leaves_other_contexts_unchanged(self):
        integration = SCRIPT.with_name("zsh-integration.zsh")
        code = '''
source "$1"
for LBUFFER in 'echo ' 'tg-send --text ' 'tg-send "' 'tg-send --url '; do
    RBUFFER=''
    PASTED=$'/tmp/a.jpg\\n/tmp/b (1).jpg'
    original=$PASTED
    _tg_send_quote_paste
    [[ $PASTED == "$original" ]] || exit 1
done
'''
        result = subprocess.run(
            ["zsh", "-f", "-c", code, "zsh", str(integration)],
            capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
