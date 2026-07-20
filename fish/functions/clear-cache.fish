function clear-cache --description "Clear all cached shell init and completions"
  cached-eval --clear
  cached-completions --clear
end
