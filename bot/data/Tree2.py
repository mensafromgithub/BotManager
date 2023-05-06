from telebot.types import InlineKeyboardMarkup, ReplyKeyboardMarkup


class Tree:
    def __init__(self, dof=(None, 0), uof=(None, 0)):
        self.twigs = dict()
        self.dof = dof
        self.uof = uof

    def make_twig(self, name=None, bot=None, user=None):
        if name:
            self.twigs[str(name)] = Twig(str(name), bot=bot if bot and not self.dof[1] else self.dof[0], user=user if user and not self.uof[1] else self.uof[0])
        else:
            self.twigs[str(len(self.twigs))] = Twig(str(len(self.twigs)), bot=bot if bot and not self.dof[1] else self.dof[0], user=user if user and not self.uof[1] else self.uof[0])

    def set_bot(self, bot):
        self.dof[0] = bot
        if self.dof[1]:
            for i in len(self):
                self.twigs[i].bot = bot

    def set_user(self, user):
        self.uof[0] = user
        if self.uof[1]:
            for i in len(self):
                self.twigs[i].set_user(user)

    def __len__(self):
        return len(self.twigs)

    def __getitem__(self, ind):
        try:
            return self.twigs[ind]
        except:
            try:
                return self.twigs[list(self.twigs.keys())[ind]]
            except:
                return None

    def __str__(self):
        return str(self.twigs)
    

class Twig:
    def __init__(self, name, bot, user):
        self.signals = dict()
        self.name = name
        self.bot = bot
        self.user = user
        self.callback_handlers = {}
        self.conditions = {}

    def __getitem__(self, ind):
        try:
            return self.signals[ind]
        except:
            try:
                return self.signals[list(self.signals.keys())[ind]]
            except:
                return None

    def __len__(self):
        return len(self.signals)
                 
    def __call__(self, data=None,  ind=0):
        try:
                sig = self.signals[ind]
                n = [i for i in range(len(self.conditions[ind])) if self.conditions[ind][i](data)]
                if not n:
                    msg = self.bot.send_message(sig[0].chat_id, 'Неверный ввод')
                    self.bot.register_next_step_handler(msg, self, ind=ind)
                else:
                    n = n[0]
                    if not isinstance(sig, Twig):
                        if sig[n].content_type == 'text':
                            msg = self.bot.send_message(list(*sig[n].values())[2:])
                            self.bot.register_next_step_handler(msg, self, ind=ind + 1)
                    else:
                        sig(ind=0)
        except:
            pass

    def __repr__(self):
        return str(self.signals)

    def __str__(self):
        return str(self.signals)

    def set_bot(self, bot):
        self.bot = bot

    def set_user(self, user):
        if user.isdigi():
            self.user = user
            for i in self.signals:
                for j in self.signals[i]:
                    self.signals[i][j].chat_id = self.user
            return True
        return False

    def make_metre(self, cont, condition=lambda x: True, keyboard=None):
        if (not isinstance(cont, Twig)) and (not isinstance(cont, Leaf)):
                return False
        if not ((keyboard != None) == (isinstance(keyboard, InlineKeyboardMarkup) or isinstance(keyboard, ReplyKeyboardMarkup))):
            return False
        if type(condition) != type(lambda: True):
            return False
        n = len(self) if len(self) > 0 else len(self) + 1
        self.conditions[n - 1] = {0: condition}
        self.signals[n - 1] = {0: cont}
        self.signals[len(self)] = lambda x: x
        self.callback_handlers[n - 1] = {0: {}}
        if keyboard != None:
            cd = [f'{n}{i[0].callback_data}' for i in keyboard.keyboard]
            for i, value in enumerate(keyboard.keyboard):
                self.callback_handlers[n - 1][0][i] = self.bot.callback_query_handler(func=lambda x: x == value[0].callback_data)(lambda: self(data=str(value[0].callback_data), ind=n))
        return True

    def replace_metre(self, cont, ind, condition=lambda x: True, keyboard=None):
        if ind not in range(len(self)):
            return False
        if (not isinstance(cont, Twig)) and (not isinstance(cont, Leaf)):
                return False
        if not ((keyboard != None) == (isinstance(keyboard, InlineKeyboardMarkup) or isinstance(keyboard, ReplyKeyboardMarkup))):
            return False
        if type(condition) != type(lambda: True):
            return False
        self.conditions[ind] = {0: condition}
        self.signals[ind] = {0: cont}
        self.callback_handlers[ind] = {0: {}}
        if keyboard != None:
            cd = [f'{n}{i[0].callback_data}' for i in keyboard.keyboard]
            for i, value in enumerate(keyboard.keyboard):
                self.callback_handlers[n - 1][0][i] = self.bot.callback_query_handler(func=lambda x: x == value[0].callback_data)(lambda: self(data=str(value[0].callback_data), ind=n))
        return True

    def switch_metre(self, switchable, switched):
        if switchable not in range(len(self)) or switched not in range(len(self)):
            return False
        self.conditions[switchable], self.conditions[switched] = self.conditions[switched], self.conditions[switchable]
        self.signals[switchable], self.signals[switched] = self.signals[switched], self.signals[switchable]
        return True

    def switch_metre_without_conds(self, switchable, switched):
        if switchable not in range(len(self)) or switched not in range(len(self)):
            return False
        if nlen(self[switchable]) != len(self[switched]):
            return False
        self.signals[switchable], self.signals[switched] = self.signals[switched], self.signals[switchable]
        return True

    def del_condition(self, ind):
        if ind not in range(len(self)):
            return False
        if len(self[ind]) != 1:
            return False
        self.conditions[ind] = {0: lambda x: True}
        return True

    def set_conditions(self, ind, conditions):
        if ind not in range(len(self)):
            return False
        if len(conditions) != len(self[ind]):
            return False
        if not all([type(i) == type(lambda x: True) for i in conditions]):
            return False
        if any([i('-300') for i in conditions]):
            return False
        self.conditions[ind] = dict([(i, v) for i, v in enumerate(conditions)])
        return True

    def set_condition(self, ind, n, condition):
        if type(condition) != type(lambda x: True):
            return False
        if ind not in range(len(self)):
            return False
        if n not in range(len(self[ind])):
            return False
        if condition('-300'):
            return False
        self.conditions[ind][n] = condition
        return True

    def switch_conditions_without_metres(self, switchable, switched):
        if switchable not in range(len(self)) or switched not in range(len(self)):
            return False
        if len(self[switchable]) != len(self[switched]):
            return False
        self.conditions[switchable], self.conditions[switched] = self.conditions[switched], self.conditions[switchable]
        return True


    def switch_conditions_without_leafs(self, ind, switchable, switched):
        if ind not in range(len(self)):
            return False
        if switchable not in range(len(self)) or switched not in range(len(self)):
            return False
        self.conditions[ind][switchable], self.conditions[ind][switched] = self.conditions[ind][switched], self.conditions[ind][switchable]
        return True

    def replace_leaf(self, cont, ind, n, condition=lambda x: True, keyboard=None):
        if ind not in range(len(self)):
            return False
        if n not in range(len(self[ind])):
            return False
        if type(condition) != type(lambda x: True):
            return False
        self.conditions[ind][n] = condition
        self.signals[ind][n] = cont
        return True

    def switch_leaf_without_conds(self, ind, switchable, switched):
        if ind not in range(len(self)):
            return False
        if switchable not in range(len(self)) or switched not in range(len(self)):
            return False
        self.signals[ind][switchable], self.signals[ind][switched] = self.signals[ind][switched], self.signals[ind][switchable]
        return True
    
    def add_leaf(self, cont, condition,  ind, keyboard=None):
            if ind not in range(len(self)):
             return False
            if (not isinstance(cont, Twig)) and (not isinstance(cont, Leaf)):
                return False
            n = len(self[ind])
            self.conditions[ind][n] = condition
            self.signals[ind][n] = cont
            self.callback_handlers[ind][n] = {}
            if keyboard != None:
                cd = [f'{n}{i[0].callback_data}' for i in keyboard.keyboard]
                for i, value in enumerate(keyboard.keyboard):
                    self.callback_handlers[ind][n][i] = self.bot.callback_query_handler(func=lambda x: x == value[0].callback_data)(lambda: self(data=str(value[0].callback_data), ind=n))
            return True

    def del_metre(self, ind):
        if ind not in range(len(self)):
            return False
        k = list(self.signals.keys())
        kc = list(self.conditions.keys())
        for i in range(ind, len(self) - 1):
            self.signals[k[i]] =  self[k[i + 1]]
            self.conditions[kc[i]] =  self.conditions[kc[i + 1]]
        del self.signals[k[-1]]
        del self.conditions[kc[-1]]
        return True

    def del_leaf(self, ind, n):
        if ind not in range(len(self)):
            return False
        if n not in range(len(self[ind])):
            return False
        k = list(self[ind].keys())
        kc = list(self.conditions[ind].keys())
        for i in range(n, len(self[ind]) - 1):
            self[ind][k[i]] =  self[ind][k[i + 1]]
            self.conditions[ind][kc[i]] =  self.conditions[ind][kc[i + 1]]
        del self[ind][k[-1]]
        del self.conditions[ind][kc[-1]]
        return True

    def set_message_handler(self):
        pass

    def set_callback_query_handler(self):
        pass

    def get_connection(self, ind=0):
        cons = ''
        for i in self.signals:
            for j in self[i]:
                cons += f'{i}.{j} -> '
        cons += ' ...'
        return cons


class Leaf:
    def __init__(self):
        self.content_type = ''
        self.condition = lambda x: True

    def __iter__(self):
        return iter(vars(self))

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return f'Lf({str(self)})'

    def set_content_type(self, content_type):
        self.content_type = content_type

    def set_condition(self, condition):
        if type(condition) != type(lambda: True):
            return False
        self.condition = condition
        return True

    def set_params(self, params: dict):
        for i in params:
            self.__setattr__(i, params[i])
        return True
