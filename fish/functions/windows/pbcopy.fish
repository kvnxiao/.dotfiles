function pbcopy --description "Copy stdin to the Windows clipboard"
  # clip.exe decodes stdin as UTF-16LE; raw UTF-8 lands as mojibake. clip.exe
  # rewrites LF and lone CR to CRLF. Redirecting to /dev/clipboard instead is
  # unreliable: writes usually exit 0 yet leave the clipboard empty, and
  # intermittently fail with EACCES.
  iconv -f UTF-8 -t UTF-16LE | clip.exe
end
