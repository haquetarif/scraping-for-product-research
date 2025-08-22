set -e

sudo apt update

# Noble (24.04) uses *t64* names for some libs
sudo apt install -y python3 python3-pip python3-venv \
  libnss3 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libxkbcommon0 \
  libasound2t64 libxcomposite1 libxrandr2 libgbm1

python3 -m venv venv
. venv/bin/activate

pip install --upgrade pip
pip install playwright pandas openpyxl

# Install browser binaries
python -m playwright install

# (Optional but recommended) Install OS deps Playwright needs
sudo "$(which python)" -m playwright install-deps

echo
echo "✅ Setup complete."
echo "   To use the environment later run:  source venv/bin/activate"
