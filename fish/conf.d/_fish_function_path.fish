# Fish probes every autoload directory on the first use of each command name;
# under MSYS2 each directory adds ~3ms to startup. Drop directories that have
# no functions.
set -l _dirs
for d in $fish_function_path
  set -l f $d/*.fish
  set -q f[1]; and set -a _dirs $d
end
set fish_function_path $_dirs
