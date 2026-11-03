# hypr-tgs

Open Telegram Desktop's share dialog from the terminal. The command is `tgs`.
Choose the recipient and confirm in Telegram; no bot or API credentials needed.

Made for Hyprland, also works on KDE and other Linux desktops.

## Requirements

- Telegram Desktop: `Telegram` or `telegram-desktop` in `PATH`.
- Bash with `mapfile -d` support (Bash 5 works), Python 3 and GNU coreutils.
- Git to clone the repository.
- Optional: zsh and a terminal with bracketed paste for pasting paths from Yazi.
- Optional: `xdg-open` or `gio` for Telegram links. Otherwise `tgs` calls
  Telegram directly. The desktop URI handler must point to Telegram when used.

## Install

```sh
git clone https://github.com/komparator147477/hypr-tgs.git ~/.local/share/hypr-tgs
mkdir -p ~/.local/bin
ln -s ~/.local/share/hypr-tgs/tgs ~/.local/bin/tgs
```

Make sure `~/.local/bin` is in your `PATH`.

For Yazi pastes, add this line to `~/.zshrc` and run it once in the current shell:

```zsh
source ~/.local/share/hypr-tgs/zsh-integration.zsh
```

Oh My Zsh is optional. Other shells can use `tgs` without this integration.

## Usage

```sh
tgs report.pdf
tgs photo.jpg "photo (1).jpg" scan.pdf
tgs --url 'https://example.com' 'Take a look'
tgs --text 'Hello'
```

With the zsh integration, type `tgs `, paste the paths copied from Yazi,
then press Enter. Each line becomes a separate quoted argument, including
names with spaces or parentheses. This also works after `tgs --file `.
Pasting into other commands keeps its normal behavior.

Without the integration, quote each path or the whole multiline list:

```sh
tgs "/home/me/photo.jpg
/home/me/photo (1).jpg"
```

| Arguments | Action |
| --- | --- |
| `FILE [FILE ...]` | Validate local files and open Telegram's share picker. |
| `--file FILE [FILE ...]` | Explicit file mode; same as passing paths directly. |
| `--url URL [TEXT]` | Open a Telegram link to share a URL with optional text. |
| `--text TEXT` | Open a Telegram text-sharing link. |
| `-h`, `--help` | Show usage. No arguments also show usage. |

Directories and missing files are rejected before Telegram opens. Quote text
and URLs containing spaces or shell characters. Link handling depends on the
installed Telegram Desktop version and URI handler.

## Update

```sh
git -C ~/.local/share/hypr-tgs pull --ff-only
```

## Uninstall

Remove the `source` line from `~/.zshrc`, then:

```sh
rm ~/.local/bin/tgs
rm -rf ~/.local/share/hypr-tgs
```

Open a new shell to unload the zsh function and paste hook.
