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
                self.twigs[i].user = user

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
    

class Twig:
    def __init__(self, name, bot, user):
        self.signals = dict()
        self.name = name
        self.bot = bot
        self.callback_handler = []
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
                if not isinstance(sig, Twig):
                    n = [i for i in range(len(self.conditions[ind])) if self.conditions[ind][i](data)]
                    if  n:
                        n = n[0]
                        if sig[n][-1] == 'text':
                            msg = self.bot.send_message(*sig[n][0].values())
                            self.bot.register_next_step_handler(msg, self, ind=ind + 1)
                    else:
                        msg = self.bot.send_message(sig[n]['chat_id'], 'Неверный ввод')
                        self.bot.register_next_step_handler(msg, self, ind=ind)
        except:
            pass

    def set_bot(self, bot):
        self.bot = bot

    def make_metre(self, msg, condition=lambda x: True, keyboard=None):
        n = len(self) if len(self) > 0 else len(self) + 1
        if type(condition) != type(lambda: True):
            return False
        if msg.content_type == 'text':
            self.conditions[n - 1] = {0: condition}
            self.signals[n - 1] = {0: ({'chat_id': msg.chat.id,
                                        'text': msg.text,
                                        'parse_mode': None,
                                        'entities': None,
                                        'disable_web_page_preview': None,
                                        'disable_notification': None,
                                        'protect_content': None,
                                        'reply_to_message_id': None,
                                        'allow_sending_without_reply': None,
                                        'reply_markup': keyboard,
                                        'timeout': None,
                                        'message_thread_id': None}, 'text')}
            self.signals[len(self)] = lambda x: x
            return True
        return False

    def replace_metre(self, msg, ind, condition=lambda x: True, keyboard=None):
        if type(condition) != type(lambda: True):
            return False
        if ind not in range(len(self)):
            return False
        if msg.content_type == 'text':
            self.conditions[ind] = {0: condition}
            self.signals[ind] = {0: ({'chat_id': msg.chat.id,
                                            'text': msg.text,
                                            'parse_mode': None,
                                            'entities': None,
                                            'disable_web_page_preview': None,
                                            'disable_notification': None,
                                            'protect_content': None,
                                            'reply_to_message_id': None,
                                            'allow_sending_without_reply': None,
                                            'reply_markup': keyboard,
                                            'timeout': None,
                                            'message_thread_id': None}, 'text')}
            return True
        return False

    def switch_metre(self, switchable, switched):
        if switchable not in range(len(self)) or switched not in range(len(self)):
            return False
        self.conditions[switchable], self.conditions[switched] = self.conditions[switched], self.conditions[switchable]
        self.signals[switchable], self.signals[switched] = self.signals[switched], self.signals[switchable]
        return True

    def switch_metre_without_conds(self, switchable, switched):
        if switchable not in range(len(self)) or switched not in range(len(self)):
            return False
        if len(self[switchable]) == len(self[switched]):
            self.signals[switchable], self.signals[switched] = self.signals[switched], self.signals[switchable]
            return True
        return False

    def del_conditions(self, ind):
        if ind not in range(len(self)):
            return False
        self.conditions[ind] = dict([(i, lambda x: True) for i in self.signals[ind]])
        return True

    def set_conditions(self, ind, conditions):
        if ind not in range(len(self)):
            return False
        if not len(conditions) != len(self[ind]):
            return False
        if not all([type(i) == type(lambda: True) for i in conditions]):
            return False
        if any([i('-300') for i in conditions]):
            return False
        self.conditions[ind] = dict([(i, v) for i, v in enumerate(conditions)])
        return True

    def set_condition(self, ind, n, condition):
        if type(condition) != type(lambda: True):
            return False
        if ind not in range(len(self)):
            return False
        if n not in range(len(self[ind])):
            return False
        if self.conditions[ind][0]('-300'):
            return False
        if condition('-300'):
            return False
        self[ind][n] = condition
        return True

    def switch_conditions_without_metres(self, switchable, switched):
        if switchable not in range(len(self)) or switched not in range(len(self)):
            return False
        if len(self[switchable]) == len(self[switched]):
            self.conditions[switchable], self.conditions[switched] = self.conditions[switched], self.conditions[switchable]
            return True
        return False


    def switch_conditions_without_leafs(self, ind, switchable, switched):
        if ind not in range(len(self)):
            return False
        if switchable not in range(len(self)) or switched not in range(len(self)):
            return False
        self.conditions[ind][switchable], self.conditions[ind][switched] = self.conditions[ind][switched], self.conditions[ind][switchable]
        return True

    def replace_leaf(self, msg, ind, n, condition=lambda x: True, keyboard=None):
        if type(condition) != type(lambda: True):
            return False
        if ind not in range(len(self)):
            return False
        if n not in range(len(self[ind])):
            return False
        if msg.content_type == 'text':
            self.conditions[ind][n] = condition
            self.signals[ind][n] = ({'chat_id': msg.chat.id,
                                        'text': msg.text,
                                        'parse_mode': None,
                                        'entities': None,
                                        'disable_web_page_preview': None,
                                        'disable_notification': None,
                                        'protect_content': None,
                                        'reply_to_message_id': None,
                                        'allow_sending_without_reply': None,
                                        'reply_markup': keyboard,
                                        'timeout': None,
                                        'message_thread_id': None}, 'text')
            return True
        return False

    def switch_leaf_without_conds(self, ind, switchable, switched):
        if ind not in range(len(self)):
            return False
        if switchable not in range(len(self)) or switched not in range(len(self)):
            return False
        self.signals[ind][switchable], self.signals[ind][switched] = self.signals[ind][switched], self.signals[ind][switchable]
        return True
    
    def add_leaf(self, twig, ind, condition):
            n = len(self[ind])
            print(twig)
            print(n)
            print(ind)
            if ind not in range(len(self)):
                return False
            if type(condition) != type(lambda: True):
                return False
            if isinstance(twig, Twig):
                if not self.conditions[ind][0]('-300'):
                    if not condition('-300'):
                        self.conditions[ind][len(self.conditions[ind])] = condition
                        self.signals[ind][n] = twig
                    return False
                else:
                    self.conditions[ind][len(self.conditions[ind])] = lambda x: True
                    self.signals[ind][n] = twig
                return True
            return False
        
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
