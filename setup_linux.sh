#!/usr/bin/bash
chmod +x setup_linux.sh

# setup virtual environment
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
pip install waitress

# Download llm
cd ./app/llm
curl -L -o llama-2-7b-chat.ggmlv3.q8_0.bin https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q8_0.bin

cd ../../

echo '#!/usr/bin/bash
chmod +x setup_linux.sh
source ./venv/bin/activate 
exec waitress-serve --listen=*:5000 --expose-tracebacks main:app' > run_app.sh
