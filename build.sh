#!/bin/bash
set -e

# colors.sh を修正
sed -i 's/$(tput setaf 1)/\\033[31m/g' /home/render/colors.sh
sed -i 's/$(tput setaf 2)/\\033[32m/g' /home/render/colors.sh
sed -i 's/$(tput sgr0)/\\033[0m/g' /home/render/colors.sh

# アプリケーションのビルドやセットアップを続行
./setup.sh