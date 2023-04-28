class Tree:
    def __init__(self, dof=(None, 0), uof=(None, 0)):
        self.twigs = dict()
        self.dof = dof
        self.uof = uof

    def make_twig(self, name=None, bot=None, user=None):
        if name:
            self.twigs[str(name)] = Twig(str(name), bot=bot if bot and not self.dof[1] else self.dof[0],
                                         user=user if user and not self.uof[1] else self.uof[0])
        else:
            self.twigs[str(len(self.twigs))] = Twig(str(len(self.twigs)),
                                                    bot=bot if bot and not self.dof[1] else self.dof[0],
                                                    user=user if user and not self.uof[1] else self.uof[0])

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
        self.user = user
        self.functions = {'text': lambda x, y, z=None: self.bot.send_message(x, y, reply_markup=z),
                          'twig': lambda x, y, z=None: y()}

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

    def __call__(self, inf=None, ind=0):
        try:
            try:
                print(inf if not inf else type(inf.text))
            except:
                print(inf)
            print(ind)
            msg = ''
            try:
                msg = self[ind](self.user, inf if not inf else inf.text)
            except:
                msg = self[ind](self.user, inf)
            print(msg)
            ind = ind if msg else ind - 1
            if ind != len(self.signals):
                self.bot.register_next_step_handler(
                    msg[-1] if msg else self.bot.send_message(inf.from_user.id, 'Неверный ввод') if inf else '', self,
                    ind + 1)
            else:
                pass
        except:
            pass

    def set_bot(self, bot):
        self.bot = bot

    def set_user(self, user):
        self.user = user

    def make_metre(self, data, conditions=None, keyboard=None):
        if not conditions:
            self.signals[str(len(self.signals) + 1)] = lambda x, y: [
                self.functions[data[i][2]](data[i][0] if data[i][0] else x, data[i][1],
                                           keyboard if i == (len(data) - 1) else None) for i in range(len(data))]
        elif self.signals:
            self.signals[str(len(self.signals) + 1)] = lambda x, y: [
                self.functions[data[i][2]](data[i][0] if data[i][0] else x, data[i][1],
                                           keyboard if i == (len(conditions) - 1) else None) for i in
                range(len(conditions)) if conditions[i](y)]