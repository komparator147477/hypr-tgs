# tg-send

Open Telegram Desktop's interactive forwarding picker for one or more local files.

```bash
tg-send file.pdf
tg-send file1.pdf "file with spaces.jpg" scan.pdf
tg-send /home/me/folder with spaces/file.pdf
```

Install through `~/.zshrc`:

```zsh
tg-send() {
    ~/coding/telegram-send/tg-send "$@"
}
```

The script validates file paths, including paths that were split on spaces by
file-manager shell integrations, resolves absolute paths, then launches Telegram
Desktop's share picker.
