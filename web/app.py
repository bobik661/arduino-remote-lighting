import os, time
from functools import wraps
from flask import Flask, jsonify, render_template, request
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me')
AGENT_TOKEN = os.environ.get('AGENT_TOKEN', '')
CONTROL_PIN = os.environ.get('CONTROL_PIN', '')
state = {'desired': False, 'reported': False, 'version': 0, 'updated_at': time.time(), 'agent_seen': None}
def agent_only(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not AGENT_TOKEN or request.headers.get('X-Agent-Token') != AGENT_TOKEN:
            return jsonify(error='Unauthorized'), 401
        return fn(*args, **kwargs)
    return wrapped
@app.get('/')
def home(): return render_template('index.html')
@app.get('/health')
def health(): return jsonify(ok=True)
@app.get('/api/state')
def get_state():
    seen = state['agent_seen']
    return jsonify(**state, connected=seen is not None and time.time()-seen < 15)
@app.post('/api/control')
def control():
    data = request.get_json(silent=True) or {}
    if not CONTROL_PIN or str(data.get('pin', '')) != CONTROL_PIN: return jsonify(error='Неверный PIN-код'), 403
    value = data.get('on')
    if not isinstance(value, bool): return jsonify(error='Поле on должно быть true или false'), 400
    state['desired'] = value; state['version'] += 1; state['updated_at'] = time.time()
    return jsonify(ok=True, version=state['version'], desired=value)
@app.get('/api/agent/command')
@agent_only
def agent_command():
    state['agent_seen'] = time.time()
    return jsonify(desired=state['desired'], version=state['version'])
@app.post('/api/agent/status')
@agent_only
def agent_status():
    data = request.get_json(silent=True) or {}
    if not isinstance(data.get('on'), bool): return jsonify(error='Invalid status'), 400
    state['reported'] = data['on']; state['agent_seen'] = time.time()
    return jsonify(ok=True)
if __name__ == '__main__': app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '5000')))
