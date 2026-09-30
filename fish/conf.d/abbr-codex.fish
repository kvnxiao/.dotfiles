if status is-interactive
  function codex --wraps codex --description 'Run Codex with local settings and platform permissions'
    set -l options --profile local
    if test "$FISH_OS" = windows
      set -a options --config 'default_permissions="windows-msys2-read"'
    end
    command codex $options $argv
  end

  set -l ASTRA_MODEL gpt-6-astra
  set -l SOL_MODEL gpt-6.1-sol
  set -l LUNA_MODEL gpt-6-luna
  set -l EFFORT_NAMES '' high med low
  set -l EFFORT_VALUES xhigh high medium low

  for effort_name in $EFFORT_NAMES
    set -l effort_value $EFFORT_VALUES[1]
    set -e EFFORT_VALUES[1]
    abbr -a "astra$effort_name" "codex --model=\"$ASTRA_MODEL\" --config model_reasoning_effort=\"$effort_value\""
    abbr -a "sol$effort_name" "codex --model=\"$SOL_MODEL\" --config model_reasoning_effort=\"$effort_value\""
    abbr -a "luna$effort_name" "codex --model=\"$LUNA_MODEL\" --config model_reasoning_effort=\"$effort_value\""
  end
end
