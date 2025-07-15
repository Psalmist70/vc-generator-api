#!/usr/bin/env bash
curl https://pyenv.run | bash

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

pyenv install 3.10.12
pyenv global 3.10.12

python --version

pip install --upgrade pip
pip install -r requirements.txt
