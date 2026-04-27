# pip fish completion start
# Vendored override of `pip completion --fish` output. The upstream version
# uses a `set ... \` line continuation followed by indented `(...)` command
# substitutions, which fish 4.0+ rejects with "command substitutions not
# allowed in command position". Collapsed onto one line here.
function __fish_complete_pip
    set -lx COMP_WORDS (commandline --current-process --tokenize --cut-at-cursor) (commandline --current-token --cut-at-cursor)
    set -lx COMP_CWORD (math (count $COMP_WORDS) - 1)
    set -lx PIP_AUTO_COMPLETE 1
    set -l completions ($COMP_WORDS[1])
    string split \  -- $completions
end
complete -fa "(__fish_complete_pip)" -c pip
# pip fish completion end
