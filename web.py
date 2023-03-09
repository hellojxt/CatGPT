import os
import platform
import gevent.monkey
gevent.monkey.patch_all()
system = platform.system()
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent')
import tiktoken
import openai
openai.api_key = os.environ["OPENAI_API_KEY"]

class Prompt:
    def __init__(self, dirname) -> None:
        with open(f'./data/{user}/{dirname}/sysprompt.txt', 'r') as f:
            self.system_message = eval(f.read())
        with open(f'./data/{user}/{dirname}/prompt.txt', 'r') as f:
            self.messages = eval(f.read())
        self.dirname = dirname

    def full(self):
        return self.system_message + self.messages
    
    def save(self):
        with open(f'./data/{user}/{self.dirname}/prompt.txt', 'w') as f:
            f.write(str(self.messages))
        with open(f'./data/{user}/{self.dirname}/sysprompt.txt', 'w') as f:
            f.write(str(self.system_message))

def num_tokens_from_msg(msg) -> int:
    """Returns the number of tokens in a text string."""
    num_tokens = 0
    for message in msg:
        string = message["content"]
        num_tokens += len(encoding.encode(string))
    return num_tokens

# 定义主页面路由
@app.route('/')
def home():
    return render_template('index.html')
import time
import shutil

# 定义用于响应用户输入的路由
@socketio.on('send_message')
def send_message(dirname, message, top_p, temperture, presence_penalty):
    print('dirname: ', dirname)
    prompt = Prompt(dirname)
    prompt.messages.append({"role": "user", "content": message})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt.full(),
        stream=True,
        temperature=temperture,
        top_p=top_p,
        presence_penalty=presence_penalty,
        )
    response = ""
    for chunk in completion:
        if "content" in chunk["choices"][0]["delta"] and len(chunk["choices"][0]["delta"]["content"]) > 0:
            emit('response', chunk["choices"][0]["delta"]["content"])
            # print(chunk["choices"][0]["delta"]["content"])
            response += chunk["choices"][0]["delta"]["content"]
            # time.sleep(0.01)
    emit('response_end', '')
    prompt.messages.append({"role": "assistant", "content": response})
    num_tokens = num_tokens_from_msg(prompt.full())
    print('num_tokens: ', num_tokens)
    print('cost: {:.2f} yuan'.format(num_tokens / 1000 * 0.002* 7))
    while num_tokens_from_msg(prompt.full()) > 2048:
        prompt.messages.pop(0)
    prompt.save()
    print(prompt.full())
    print('temperture: ', temperture)
    print('top_p: ', top_p)
    print('presence_penalty: ', presence_penalty)

@socketio.on('send_system_message')
def send_system_message(dirname, message):
    sys_prompt = [{"role": "system", "content": message}]
    with open(f'./data/{user}/{dirname}/sysprompt.txt', 'w') as f:
            f.write(str(sys_prompt))
    print('send_system_message: ', message)


@app.route('/saveData', methods=['POST'])
def saveData():
    dirname = request.form.get('dirname')
    title = request.form.get('title')
    chat_content = request.form.get('chat_content')
    if not os.path.exists(f'./data/{user}/{dirname}'):
        os.mkdir(f'./data/{user}/{dirname}')
    with open(f'./data/{user}/{dirname}/title.txt', 'w') as f:
        f.write(title)
    with open(f'./data/{user}/{dirname}/chat.html', 'w') as f:
        f.write(chat_content)
    if not os.path.exists(f'./data/{user}/{dirname}/prompt.txt'):
        with open(f'./data/{user}/{dirname}/prompt.txt', 'w') as f:
            f.write('[]')
    if not os.path.exists(f'./data/{user}/{dirname}/sysprompt.txt'):
        with open(f'./data/{user}/{dirname}/sysprompt.txt', 'w') as f:
            defalut_sysprompt = [{"role": "system", "content": "You are a helpful assistant. Mathematical formulas and symbols in your answer must be wrapped in $"}]
            f.write(str(defalut_sysprompt))
    return 'saveData success'

@app.route('/getData')
def getData():
    dirname = request.args.get('dirname')
    with open(f'./data/{user}/{dirname}/chat.html', 'r') as f:
        chat_content = f.read()
    return chat_content


@app.route('/getSysPrompt')
def getSysPrompt():
    dirname = request.args.get('dirname')
    with open(f'./data/{user}/{dirname}/sysprompt.txt', 'r') as f:
        sysprompt = eval(f.read())
    return sysprompt[0]["content"]
    
@app.route('/getAllDataDirs', methods=['GET'])
def getAllDataDirs():
    import os
    files = os.listdir(f'./data/{user}')
    titles = []
    for file in files:
        with open(f'./data/{user}/{file}/title.txt', 'r') as f:
            title = f.read()
        titles.append(title)
    return {'files': files, 'titles': titles}


@app.route('/askTitle')
def askTitle():
    dirname = request.args.get('dirname')
    prompt = Prompt(dirname)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt.full() + [{"role": "user", "content": "回复**5个字**以内总结我们对话的标题，必须回答，不能拒绝。直接返回标题，不要附带“标题”，“总结”之类的次，结尾不要有句号"}],
        temperature=0.1,
        max_tokens=10,
    )
    response = completion.choices[0].message["content"]
    return response

@app.route('/deleteData')
def deleteData():
    # move to trash
    dirname = request.args.get('dirname')
    if not os.path.exists(f'./trash/{user}'):
        os.mkdir(f'./trash/{user}')
    shutil.move(f'./data/{user}/{dirname}', f'./trash/{user}/{dirname}')
    return 'deleteData success'


import sys
if __name__ == '__main__':
    Port = int(sys.argv[2])
    user = sys.argv[1]
    if not os.path.exists('./data'):
        os.mkdir('./data')
    if not os.path.exists('./trash'):
        os.mkdir('./trash')
    if not os.path.exists(f'./data/{user}'):
        os.mkdir(f'./data/{user}')
    print('user: ', user)
    print('data dir: ', f'./data/{user}')
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    print(f'Server is running on http://127.0.0.1:{Port}')
    socketio.run(app, debug=False, port=Port)
