function pbpaste --description "Print the Windows clipboard with LF line endings"
  # clip.exe is write-only; /dev/clipboard reads are byte-exact and uncapped.
  # Windows stores CRLF. sed strips CR only at line ends and preserves lone CRs
  # embedded mid-line, where tr -d would delete them.
  sed 's/\r$//' < /dev/clipboard
end
