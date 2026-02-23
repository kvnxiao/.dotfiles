function mpv --description "Run mpv.exe detached"
    command mpv.exe $argv &
    disown
end
