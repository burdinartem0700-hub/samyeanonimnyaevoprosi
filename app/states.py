from aiogram.fsm.state import State, StatesGroup

class idea(StatesGroup):
    idea_text = State()

class Premium(StatesGroup):
    add_premka = State()
    del_premka = State()
    id_state = State()
    first_state = State()
    username_state = State()

class StaticState(StatesGroup):
    userid = State()
    referid = State()
    send = State()
    rec = State()
    refer = State()

class Edits(StatesGroup):
    eid = State()
    ed_user_id = State()