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

    def make_metre(self, msg, conditions=[lambda x: True], keyboard=None):
        if msg.content_type == 'text':
            self.conditions[len(self)] = conditions
            self.signals[len(self) - 1] = {0: ({'chat_id': msg.chat.id,
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

    def replace_metre(self, msg, ind, conditions=[lambda x: True], keyboard=None):
        if msg.content_type == 'text':
            self.conditions[ind] = conditions
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
    
    def add_metre(self, twig, ind):
            n = len(self[ind])
            print(twig)
            print(n)
            print(ind)
            self.signals[ind][n] = twig
        
    def del_metre(self, ind):
        k = list(self.signals.keys())
        for i in range(ind, len(self) - 1):
            self.signals[k[i]] =  self[k[i + 1]]
        del self.signals[k[-1]]

    def del_leaf(self, ind, n):
        k = list(self[ind].keys())
        for i in range(ind, len(self) - 1):
            self[ind][k[i]] =  self[ind][k[i + 1]]
        del self[ind][k[-1]]