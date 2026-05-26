# telegram-send

Open Telegram Desktop's interactive forwarding picker for one or more local files.

```bash
telegram-send file.pdf
telegram-send file1.pdf "file with spaces.jpg" scan.pdf
```

Install through `~/.zshrc`:

```zsh
telegram-send() {
    ~/coding/telegram-send/telegram-send "$@"
}
```

The script validates that every argument is an existing regular file, resolves
absolute paths, then tries desktop integration first (`gio`, then KDE tools) and
falls back to launching Telegram Desktop directly.
