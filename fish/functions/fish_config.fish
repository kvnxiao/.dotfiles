function fish_config --wraps fish_config
  # Skip the no-op theme init fish runs on every interactive startup.
  # Colors are already set as universal variables, so this call does nothing.
  # Saves a few milliseconds on every shell startup, especially on MSYS2
  if contains -- --no-override $argv
    return 0
  end
  # For real invocations, erase this wrapper and fall through to the builtin
  functions -e fish_config
  fish_config $argv
end
