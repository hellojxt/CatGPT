call conda activate chatgpt
set http_proxy=http://127.0.0.1:7890 & set https_proxy=http://127.0.0.1:7890
start /B python web.py username 2333
start http://127.0.0.1:2333
pause