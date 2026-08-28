if status is-interactive
  set -l SOL_MODEL gpt-5.6-sol
  set -l TERRA_MODEL gpt-5.6-terra
  set -l LUNA_MODEL gpt-5.6-luna
  set -l EFFORT_NAMES '' high med low
  set -l EFFORT_VALUES xhigh high med low

  for effort_index in (seq (count $EFFORT_NAMES))
    set -l effort_name $EFFORT_NAMES[$effort_index]
    set -l effort_value $EFFORT_VALUES[$effort_index]
    abbr -a "sol$effort_name" "codex --model=\"$SOL_MODEL\" --config model_reasoning_effort=\"$effort_value\""
    abbr -a "terra$effort_name" "codex --model=\"$TERRA_MODEL\" --config model_reasoning_effort=\"$effort_value\""
    abbr -a "luna$effort_name" "codex --model=\"$LUNA_MODEL\" --config model_reasoning_effort=\"$effort_value\""
  end
end
