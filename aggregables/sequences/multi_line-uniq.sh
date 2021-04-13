#!/usr/bin/env bash

process() {
  sed 's/\([\\[:space:]'"'"']\)/\\\1/g' | \
    xargs printf '%s\f%s\n' | \
    uniq | \
    sed 's/\f/\n/g; s/\\\([\\[:space:]'"'"']\)/\1/g'
}

uniq_passes() {
  first_pass=$(uniq | process)

  # Using a sliding window of size 2,
  # do a second pass to account for
  # new repeated blocks that appeared
  # after the first pass
  printf '%s\n%s' \
    "$(echo "$first_pass" | \
      head -n1)" \
    "$(echo "$first_pass" | \
      tail -n +2 | \
      process)"
}

input=${1:-}
if [ -f "$input" ]; then
  out=$(uniq_passes < "$input")
elif [ -n "$input" ]; then
  out=$(printf '%s' "$input" | uniq_passes)
else
  out=$(uniq_passes)
fi
before_empty_dir_prune=0
after_empty_dir_prune=$(printf '%s' "$out" | wc -l)
while [ "$before_empty_dir_prune" != "$after_empty_dir_prune" ]; do
  before_empty_dir_prune=$after_empty_dir_prune
  out=$(printf '%s' "$out" | uniq_passes)
  after_empty_dir_prune=$(printf '%s' "$out" | wc -l)
done

printf '%s' "$out"
