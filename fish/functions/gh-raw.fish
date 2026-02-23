function gh-raw --description "Download raw file from GitHub: gh-raw owner/repo ref path"
  curl -sL "https://raw.githubusercontent.com/$argv[1]/$argv[2]/$argv[3]"
end
