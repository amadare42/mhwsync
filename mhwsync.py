import sys
import os
import json
import typing
from flask import Flask, request
from atatus.contrib.flask import Atatus

if sys.version_info[0] < 3 or sys.version_info[1] < 8:
    raise Exception("Python 3.8 or higher required")

app = Flask(__name__)

app.config['ATATUS'] = {
    'APP_NAME': os.environ['ATATUS_APP_NAME'],
    'LICENSE_KEY': os.environ['ATATUS_LICENSE_KEY']
}
atatus = Atatus(app)


class Globals:
    bufferSize = 50
    api_version = 2


"""
status codes:
0 - OK
1 - session does not exist
2 - session already exists
3 - invalid monster index
4 - part does not exist
5 - ailment does not exist
10 - exception
404 - HTTP 404
"""


class Status:
    ok = {
        "status": 0,
        "value": ""
    }
    sessionDoesNotExist = {
        "status": 1,
        "value": "session does not exist"
    }
    sessionAlreadyExists = {
        "status": 2,
        "value": "session already exists"
    }
    monsterOutsideRange = {
        "status": 3,
        "value": "monster outside range"
    }
    partOutsideRange = {
        "status": 4,
        "value": "part outside range"
    }
    ailmentOutsideRange = {
        "status": 5,
        "value": "ailment outside range"
    }
    e404 = {
        "status": 404,
        "value": ""
    }


class Part:
    current_hp = 0
    max_hp = 0
    times_broken = 0


class Ailment:
    current_buildup = 0
    max_buildup = 0


class Monster:
    parts: list
    ailments: list

    def __init__(self):
        self.parts = list()
        self.ailments = list()
        for _ in range(Globals.bufferSize):
            self.parts.append(Part())
            self.ailments.append(Ailment())

    def clear(self):
        for i in range(Globals.bufferSize):
            self.parts[i] = Part()
            self.ailments[i] = Ailment()


class Session:
    def __init__(self):
        self.monsters = [Monster(), Monster(), Monster()]


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Part):
            return {"current_hp": obj.current_hp, "max_hp": obj.max_hp, "times_broken": obj.times_broken}
        if isinstance(obj, Ailment):
            return {"current_buildup": obj.current_buildup, "max_buildup": obj.max_buildup}
        if isinstance(obj, Monster):
            return {"parts": obj.parts, "ailments": obj.ailments}
        if isinstance(obj, Session):
            return {"monsters": obj.monsters}

        return json.JSONEncoder.default(self, obj)


sessions = dict()


@app.route('/')
def alive():
    Status.ok["value"] = ""
    return Status.ok


@app.route('/version')
def version():
    Status.ok["value"] = Globals.api_version
    return Status.ok


@app.route('/session/<string:session>/exists')
def session_info(session: str):
    if session in sessions:
        Status.ok["value"] = ""
        return Status.ok
    return Status.sessionDoesNotExist


@app.route('/session/<string:session>/create')
def create_session(session: str):
    if session in sessions:
        return Status.sessionAlreadyExists

    sessions[session] = Session()
    Status.ok["value"] = ""
    return Status.ok


@app.route('/session/<string:session>/delete')
def delete_session(session: str):
    if session not in sessions:
        return Status.sessionDoesNotExist

    sessions.pop(session)
    Status.ok["value"] = ""
    return Status.ok


@app.route('/session/<string:session>/')
def get_session(session: str):
    if not session in sessions:
        return Status.sessionDoesNotExist

    Status.ok["value"] = json.dumps(sessions[session], cls=CustomEncoder)
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/')
def get_monster(session: str, index: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange

    Status.ok["value"] = json.dumps(sessions[session].monsters[index], cls=CustomEncoder)
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/clear')
def clear_monster(session: str, index: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange

    sessions[session].monsters[index].clear()
    Status.ok["value"] = ""
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/part/<int:part_index>/')
def get_part(session: str, index: int, part_index: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if part_index not in range(Globals.bufferSize):
        return Status.partOutsideRange

    Status.ok["value"] = json.dumps(sessions[session].monsters[index].parts[part_index], cls=CustomEncoder)
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/part/<int:part_index>/current_hp')
def get_current_part_hp(session: str, index: int, part_index: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if part_index not in range(Globals.bufferSize):
        return Status.partOutsideRange

    Status.ok["value"] = str(sessions[session].monsters[index].parts[part_index].current_hp)
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/part/<int:part_index>/current_hp/<int:value>')
def set_current_part_hp(session: str, index: int, part_index: int, value: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if part_index not in range(Globals.bufferSize):
        return Status.partOutsideRange

    sessions[session].monsters[index].parts[part_index].current_hp = value
    Status.ok["value"] = ""
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/part/<int:part_index>/max_hp')
def get_max_part_hp(session: str, index: int, part_index: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if part_index not in range(Globals.bufferSize):
        return Status.partOutsideRange

    Status.ok["value"] = str(sessions[session].monsters[index].parts[part_index].max_hp)
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/part/<int:part_index>/max_hp/<int:value>')
def set_max_part_hp(session: str, index: int, part_index: int, value: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if part_index not in range(Globals.bufferSize):
        return Status.partOutsideRange

    sessions[session].monsters[index].parts[part_index].max_hp = value
    Status.ok["value"] = ""
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/part/<int:part_index>/times_broken')
def get_part_times_broken(session: str, index: int, part_index: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if part_index not in range(Globals.bufferSize):
        return Status.partOutsideRange

    Status.ok["value"] = str(sessions[session].monsters[index].parts[part_index].times_broken)
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/part/<int:part_index>/times_broken/<int:value>')
def set_part_times_broken(session: str, index: int, part_index: int, value: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if part_index not in range(Globals.bufferSize):
        return Status.partOutsideRange

    sessions[session].monsters[index].parts[part_index].times_broken = value
    Status.ok["value"] = ""
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/part/<int:part_index>/set_all/<int:current_hp>/<int:max_hp>/<int:times_broken>/')
def set_part(session: str, index: int, part_index: int, current_hp: int, max_hp: int, times_broken: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if part_index not in range(Globals.bufferSize):
        return Status.partOutsideRange

    sessions[session].monsters[index].parts[part_index].current_hp = current_hp
    sessions[session].monsters[index].parts[part_index].max_hp = max_hp
    sessions[session].monsters[index].parts[part_index].times_broken = times_broken

    Status.ok["value"] = ""
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/ailment/<int:ailment_index>/')
def get_ailment(session: str, index: int, ailment_index: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if ailment_index not in range(Globals.bufferSize):
        return Status.ailmentOutsideRange

    Status.ok["value"] = json.dumps(sessions[session].monsters[index].ailments[ailment_index].get_all(), cls=CustomEncoder)
    return Status.ok

@app.route('/session/<string:session>/monster/<int:index>/ailment/<int:ailment_index>/current_buildup')
def get_current_ailment_buildup(session: str, index: int, ailment_index: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if ailment_index not in range(Globals.bufferSize):
        return Status.ailmentOutsideRange

    Status.ok["value"] = str(sessions[session].monsters[index].ailments[ailment_index].current_buildup)
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/ailment/<int:ailment_index>/current_buildup/<int:value>')
def set_current_ailment_buildup(session: str, index: int, ailment_index: int, value: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if ailment_index not in range(Globals.bufferSize):
        return Status.ailmentOutsideRange

    sessions[session].monsters[index].ailments[ailment_index].current_buildup = value
    Status.ok["value"] = ""
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/ailment/<int:ailment_index>/max_buildup')
def get_max_ailment_buildup(session: str, index: int, ailment_index: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if ailment_index not in range(Globals.bufferSize):
        return Status.ailmentOutsideRange

    Status.ok["value"] = str(sessions[session].monsters[index].ailments[ailment_index].max_buildup)
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/ailment/<int:ailment_index>/max_buildup/<int:value>')
def set_max_ailment_buildup(session: str, index: int, ailment_index: int, value: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if ailment_index not in range(Globals.bufferSize):
        return Status.ailmentOutsideRange

    sessions[session].monsters[index].ailments[ailment_index].max_buildup = value
    Status.ok["value"] = ""
    return Status.ok


@app.route('/session/<string:session>/monster/<int:index>/ailment/<int:ailment_index>/set_all/<int:current>/<int:max>/')
def set_ailment(session: str, index: int, ailment_index: int, current: int, max: int):
    if session not in sessions:
        return Status.sessionDoesNotExist
    if index not in range(3):
        return Status.monsterOutsideRange
    if ailment_index not in range(Globals.bufferSize):
        return Status.ailmentOutsideRange

    sessions[session].monsters[index].ailments[ailment_index].current_buildup = current
    sessions[session].monsters[index].ailments[ailment_index].max_buildup = max
    Status.ok["value"] = ""
    return Status.ok


@app.errorhandler(404)
def not_found():
    Status.e404["value"] = request.url
    return Status.e404


@app.errorhandler(Exception)
def handle_exception(e: Exception):      
    msg = {
        "status": 10,
        "value": repr(e) + ", request: " + request.full_path
    }
    app.log_exception(e)
    return msg
    

if __name__ == "__main__":
    app.run()
