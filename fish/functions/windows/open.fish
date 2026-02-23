function open --description "Open file or directory in Windows Explorer"
    explorer.exe (cygpath -w $argv)
end
