# LM_REMOTE
Local LLM chatbot web interface using Python backend.

## Python Dependencies
- `flask`
- `requests`
```bash
pip3 install -r requirements.txt
```

## Run Server
After starting a local server, e.g. using LM Studio, run
```
cd src
python3 app.py
```

## Remote Access
```bash
http://<ip-address>:5000
```

## Run Proxy Server
```bash
python forward_connections.py --src-port 8889 --dst-ip <server-ip> --dst-port 8889
```

## Browser Access
[my_url.com:8889]()