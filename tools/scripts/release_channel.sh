#!/usr/bin/env bash
# Prints "latest" for a stable tag vX.Y.Z and "prerelease" for vX.Y.Z(a|b|rc)N.
# Fails when the tag has another form or does not match the version in manifest.json.
set -euo pipefail
tag="$1"
manifest="${2:-custom_components/shoebox/manifest.json}"
version=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["version"])' "$manifest")
if [ "$tag" != "v$version" ]; then
  echo "tag $tag does not match manifest.json version $version" >&2
  exit 1
fi
if [[ "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo latest
elif [[ "$tag" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(a|b|rc)[0-9]+$ ]]; then
  echo prerelease
else
  echo "tag $tag is neither vX.Y.Z nor vX.Y.Z(a|b|rc)N" >&2
  exit 1
fi
