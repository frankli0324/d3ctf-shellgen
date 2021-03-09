from docker import DockerClient, types
from flask import Flask, render_template, request, session
from flask_apscheduler import APScheduler
from requests.exceptions import RequestException
from os import path, environ, urandom, remove, makedirs, chown
from queue import Queue
from threading import Thread
import random
import string
import os
import base64

client = DockerClient()
app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(16)
queue = Queue(maxsize=10)


def random_str():
    return ''.join([
        random.choice(string.ascii_lowercase)
        for _ in range(20)
    ])


def waf(phpshell):
    if not phpshell.startswith(b'<?php'):
        return False
    phpshell = phpshell[6:]
    for c in phpshell:
        if c not in b'0-9$_;+[].<?=>':
            return False
    return True


def run_container(image, command, mounts=None):
    container = client.containers.run(
        image, command,
        mounts=mounts,
        read_only=True,
        detach=True,
        labels={'evaluate': '1'},
        network='none',
        mem_limit=1024 * 1024 * 100
    )
    try:
        container.wait(timeout=5)
        res = container.logs()
    except RequestException:
        container.kill()
        return 'timeout'
    finally:
        container.remove()
    return res


def gen_shell(answer, path):
    try:
        result = run_container(
            'python', f'sh -c "echo -n {answer} | python /opt/gen.py"',
            [types.Mount(
                type='bind',
                source=path,
                target='/opt/gen.py',
            )])
        return result
    except Exception as e:
        return b''


def put_result(token, s):
    with open(path.join('workdir', token, 'result'), 'w') as f:
        f.write(s)


def evaluate(token, code):
    answer = random_str()

    try:
        makedirs(path.join('workdir', token), exist_ok=True)
        with open(path.join('workdir', token, 'gen.py'), 'w') as f:
            f.write(code)
    except (NotADirectoryError, FileExistsError):
        put_result(token, 'context creation failed')
        return

    try:
        shell = gen_shell(answer, path.join(environ['APP_DIR'], 'workdir', token, 'gen.py'))
        stdshell = gen_shell(answer, environ['STD_FILE'])
    except:
        stdshell = b''
        shell = b''

    if not waf(shell):
        put_result(token, 'D3t3ct3d')
        return

    result = run_container(
        'php:7-cli',
        f'sh -c "echo -n {base64.b64encode(shell).decode()}| base64 -d | php"')

    if result == 'timeout':
        put_result(token, 'Bad shell, timed out.')
        return  # 题目貌似忘return了，于是超时的脚本应该都会返回wrong answer，dbq

    if answer.encode() == result:
        if len(stdshell) < len(shell):
            put_result(
                token,
                'Great, your shell produced the correct results\n'
                'However, it\'s too long, try harder?')
        else:
            put_result(
                token,
                'Are you the master of coding? \n'
                'Good to hear that you solved this, but this is a web challenge.\n'
                'Maybe you should try shellgen2 which is a misc challenge.')
    else:
        put_result(token, 'Wr0ng Answ3r')


@app.route('/')
def index():
    return '''
<!DOCTYPE html>

<body>
    <form method="POST" action="/submit">
        <label for="code">Code:</label><br>
        <textarea name="code" id="code">Enter text here...</textarea>
        <input type="submit" value="Submit">
    </form>
</body>
'''.strip()


@app.route('/submit', methods=['POST'])
def submit():
    token = request.host.split('.')[0]
    if not token:
        return 'invalid team token'
    session['token'] = token
    try:
        if request.form.get('code', ''):
            queue.put({
                'token': token,
                'code': request.form.get('code')
            })
        else:
            return 'Where\'s your code?'
    except queue.Full:
        return 'please resubmit a few seconds later, the job queue is currently full.'
    return 'visit <a href="/result">page</a> for results'


@app.route('/result')
def result():
    token = session.get('token', '')
    if not token:
        return 'token not set'
    if path.exists(path.join('workdir', token, 'result')):
        result = open(path.join('workdir', token, 'result')).read()
        remove(path.join('workdir', token, 'result'))
        return result
    else:
        return 'wait for a sec...<script>setTimeout(()=>location.reload(), 1000);</script>'


def poll():
    for container in client.containers.list(filters={'label': f'evaluate=1'}):
        container.kill()
        container.remove()
    if queue.empty():
        return
    job = queue.get()
    thread = Thread(target=evaluate, args=[job['token'], job['code']])
    thread.start()


scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
scheduler.add_job(id='executor', func=poll, trigger="interval", seconds=10)
app.run('0.0.0.0')
