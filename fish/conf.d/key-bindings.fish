# Editor-like text selection bindings
if status is-interactive
  function __fish_start_selection
    if not set -q __fish_selection_active
      set -g __fish_selection_active 1
      commandline -f begin-selection
    end
  end

  function __fish_end_selection
    set -e __fish_selection_active
    commandline -f end-selection
  end

  function __fish_clear_selection --on-event fish_preexec
    set -e __fish_selection_active
  end

  # Character selection: Shift+Left/Right
  bind \e\[1\;2D '__fish_start_selection; commandline -f backward-char'
  bind \e\[1\;2C '__fish_start_selection; commandline -f forward-char'

  # Word selection: Ctrl+Shift+Left/Right
  bind \e\[1\;6D '__fish_start_selection; commandline -f backward-word'
  bind \e\[1\;6C '__fish_start_selection; commandline -f forward-word'

  # Line selection: Shift+Home/End
  bind \e\[1\;2H '__fish_start_selection; commandline -f beginning-of-line'
  bind \e\[1\;2F '__fish_start_selection; commandline -f end-of-line'

  # Plain movement ends selection
  bind \e\[D '__fish_end_selection; commandline -f backward-char'
  bind \e\[C '__fish_end_selection; commandline -f forward-char'
  bind \e\[1\;5D '__fish_end_selection; commandline -f backward-word'
  bind \e\[1\;5C '__fish_end_selection; commandline -f forward-word'
  bind \e\[H '__fish_end_selection; commandline -f beginning-of-line'
  bind \e\[F '__fish_end_selection; commandline -f end-of-line'

  # Backspace/Delete: kill selection if active, otherwise normal behavior
  bind \x7f __editor_backspace
  bind \e\[3~ __editor_delete
end
