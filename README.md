# tg-send

Open Telegram Desktop's interactive forwarding picker for one or more local files.

```bash
tg-send file.pdf
tg-send file1.pdf "file with spaces.jpg" scan.pdf
tg-send /home/me/folder with spaces/file.pdf
```

In zsh with the integration below, type `tg-send `, paste the paths copied from
Yazi, and press Enter. The paste is converted to separate quoted arguments,
including names with spaces and parentheses. Other commands keep their normal
paste behavior.

A quoted multiline list also works:

```bash
tg-send "/home/me/photo.jpg
/home/me/photo (1).jpg"
```

Install through `~/.zshrc`:

```zsh
source ~/coding/telegram-send/zsh-integration.zsh
```


The script validates file paths, including paths that were split on spaces by
file-manager shell integrations, resolves absolute paths, then launches Telegram
Desktop's share picker.

Run the tests with Bash, zsh and Python 3 installed:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```
