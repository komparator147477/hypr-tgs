# Quote file-manager pastes before zsh parses newlines or filename patterns.
_tg_send_quote_paste() {
    emulate -L zsh
    [[ -z $RBUFFER && $LBUFFER =~ '^[[:blank:]]*tg-send[[:blank:]]+(--file[[:blank:]]+)?$' ]] || return 0

    local line
    local -a paths=() quoted=()
    if [[ -f $PASTED ]]; then
        paths=("$PASTED")
    else
        # Leave pasted shell options and ordinary shell syntax alone.
        [[ $PASTED == *$'\n'* ]] || return 0
        for line in "${(@f)PASTED}"; do
            [[ -e $line ]] || line=${line%$'\r'}
            [[ -n $line ]] || continue
            [[ $line == /* || $line == ./* || $line == ../* || -f $line ]] || return 0
            paths+=("$line")
        done
    fi
    (( ${#paths} )) || return 0
    for line in "${paths[@]}"; do
        quoted+=("${(q)line}")
    done
    PASTED="${(j: :)quoted}"
    return 0
}

tg-send() {
    # %x is the file defining this function, even when sourced elsewhere.
    local script_dir=${${(%):-%x}:A:h}
    "$script_dir/tg-send" "$@"
}

autoload -Uz bracketed-paste-magic
# Oh My Zsh already installs this widget. Preserve any plugin wrappers.
if [[ ${widgets[bracketed-paste]-} == builtin ]]; then
    zle -N bracketed-paste bracketed-paste-magic
fi

() {
    local -a hooks=()
    zstyle -a :bracketed-paste-magic paste-finish hooks
    if (( ! ${hooks[(Ie)_tg_send_quote_paste]} )); then
        zstyle :bracketed-paste-magic paste-finish "${hooks[@]}" _tg_send_quote_paste
    fi
}
