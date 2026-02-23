function unzip --description "Extract archive, with --jis flag for Shift-JIS encoding"
    argparse 'jis' -- $argv
    or return 1

    if set -q _flag_jis
        7z x $argv -mcp=932
    else
        7z x $argv
    end
end
