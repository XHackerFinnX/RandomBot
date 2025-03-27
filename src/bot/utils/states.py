from aiogram.fsm.state import State, StatesGroup

class Post(StatesGroup):
    text_post = State()
    confirmation = State()
    
class Channel(StatesGroup):
    channel = State()