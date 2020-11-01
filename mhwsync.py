import sys
import os

from flask import Flask, request
# from atatus.contrib.flask import Atatus

if sys.version_info[0] < 3 or sys.version_info[1] != 8:
    raise Exception("Python 3.8 required")

app = Flask(__name__)


# app.config['ATATUS'] = {
#     'APP_NAME': os.environ['ATATUS_APP_NAME'],
#     'LICENSE_KEY': os.environ['ATATUS_LICENSE_KEY']
# }
# atatus = Atatus(app)

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

bufferSize = 50


class Monster:
    def __init__(self):
        self.__parts = dict()
        self.__ailments = dict()
        for i in range(bufferSize):
            self.__parts[i] = 0
            self.__ailments[i] = 0

    def clear(self):
        for i in range(bufferSize):
            self.__parts[i] = 0
            self.__ailments[i] = 0

    def get_part(self, index):
        if len(self.__parts) < index + 1:
            return None
        return self.__parts[index]

    def get_ailment(self, index):
        if len(self.__ailments) < index + 1:
            return None
        return self.__ailments[index]

    def set_part_hp(self, index, hp):
        self.__parts[index] = hp

    def set_ailment_buildup(self, index, hp):
        self.__ailments[index] = hp


class Session:
    def __init__(self):
        self.__monsters = [Monster(), Monster(), Monster()]

    def clear_monster(self, index):
        self.__monsters[index].clear()

    def get_monster(self, index):
        return self.__monsters[index]


sessions = []
session_dict = dict()


@app.route('/')
def alive():
    ok["value"] = ""
    return ok


@app.route('/session/<string:session>/exists')
def session_info(session):
    if session in session_dict:
        ok["value"] = ""
        return ok
    return sessionDoesNotExist


@app.route('/session/<string:session>/create')
def create_session(session):
    if session in session_dict:
        return sessionAlreadyExists
    index = len(sessions)
    sessions.append(Session())
    sessions[index].id = session
    session_dict[session] = index
    ok["value"] = ""
    return ok


@app.route('/session/<string:session>/delete')
def delete_session(session):
    if session not in session_dict:
        return sessionDoesNotExist
    sessions.remove(sessions[session_dict[session]])
    session_dict.pop(session)
    ok["value"] = ""
    return ok


@app.route('/session/<string:session>/monster/<int:index>/clear')
def clear_monster(session, index):
    if session not in session_dict:
        return sessionDoesNotExist
    if index not in range(3):
        return monsterOutsideRange
    session = sessions[session_dict[session]]
    session.clear_monster(index)
    ok["value"] = ""
    return ok


@app.route('/session/<string:session>/monster/<int:index>/part/<int:part_index>/hp')
def get_part_hp(session, index, part_index):
    if session not in session_dict:
        return sessionDoesNotExist
    if index not in range(3):
        return monsterOutsideRange
    if part_index not in range(bufferSize):
        return partOutsideRange
    mon = sessions[session_dict[session]].get_monster(index)
    part = mon.get_part(part_index)
    if part is None:
        return partOutsideRange
    ok["value"] = str(part)
    return ok


@app.route('/session/<string:session>/monster/<int:index>/part/<int:part_index>/hp/<int:value>')
def set_part_hp(session, index, part_index, value):
    if session not in session_dict:
        return sessionDoesNotExist
    if index not in range(3):
        return monsterOutsideRange
    if part_index not in range(bufferSize):
        return partOutsideRange
    mon = sessions[session_dict[session]].get_monster(index)
    mon.set_part_hp(part_index, value)
    ok["value"] = ""
    return ok


@app.route('/session/<string:session>/monster/<int:index>/ailment/<int:ailment_index>/buildup')
def get_ailment_buildup(session, index, ailment_index):
    if session not in session_dict:
        return sessionDoesNotExist
    if index not in range(3):
        return monsterOutsideRange
    if ailment_index not in range(bufferSize):
        return ailmentOutsideRange
    mon = sessions[session_dict[session]].get_monster(index)
    ailment = mon.get_ailment(ailment_index)
    if ailment is None:
        return ailmentOutsideRange
    ok["value"] = str(ailment)
    return ok


@app.route('/session/<string:session>/monster/<int:index>/ailment/<int:ailment_index>/buildup/<int:value>')
def set_ailment_buildup(session, index, ailment_index, value):
    if session not in session_dict:
        return sessionDoesNotExist
    if index not in range(3):
        return monsterOutsideRange
    if ailment_index not in range(bufferSize):
        return ailmentOutsideRange
    mon = sessions[session_dict[session]].get_monster(index)
    mon.set_ailment_buildup(ailment_index, value)
    ok["value"] = ""
    return ok


@app.errorhandler(404)
def not_found():
    e404["value"] = request.url
    return e404


@app.errorhandler(Exception)
def handle_exception(e, source="app-errorhandler"):
    msg = {
        "status": 10,
        "value": repr(e) + ", source: " + source + ", request: " + request.full_path
    }
    return msg


if __name__ == "__main__":
    app.run()
