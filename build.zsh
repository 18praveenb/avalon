#!/usr/bin/env zsh
rm -rv avalon-client/build
rm -rv avalon-server/static
cd avalon-client; yarn build; cd ..
cp -r avalon-client/build avalon-server/static
mv avalon-server/static/static/* avalon-server/static
