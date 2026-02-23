# Support automatically reading from fish/functions/hooks directory
# for function definitions that should be loaded before config.fish
set -p fish_function_path $__fish_config_dir/functions/hooks
