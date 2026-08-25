# MSYS2 fish cannot exec the `C:\...\just.exe` absolute path that
# `JUST_COMPLETE=fish just` hardcodes into the completion script it emits.
# The bare command name resolves through PATH.
complete --keep-order --exclusive --command just --arguments "(JUST_COMPLETE=fish just -- (commandline --current-process --tokenize --cut-at-cursor) (commandline --current-token))"
