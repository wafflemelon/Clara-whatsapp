import logging

class UnimplementedError(Exception):
    pass
    
class DuplicateWarning(Warning):
    pass

class Command:
    """ A command class to provide methods we can use with it """

    def __init__(self, bot, comm, *, alias=None, desc="",
                 admin=False, unprefixed=False, listed=True):
        self.bot = bot
        self.layer = bot.layer
        self.comm = comm
        self.desc = desc
        self.alias = alias or []
        self.admin = admin
        self.listed = listed
        self.unprefixed = unprefixed
        self.subcommands = []
        bot.commands[comm] = self
        for a in self.alias:
            if a in bot.commands:
                raise DuplicateWarning("Duplicate command name: " + a)
            else:
                bot.commands[a] = self

    def subcommand(self, *args, **kwargs):
        """ Create subcommands """
        return SubCommand(self, *args, **kwargs)


    def __call__(self, func):
        """ Make it a decorator """

        self.func = func

        return self

    def run(self, message):
        """ Does type checking for command arguments """
        logging.debug("Runing command: {}".format(self.comm))
        
        if not self.layer:
            self.layer = bot.layer

        args = message.getBody().split(" ")[1:]

        args_name = inspect.getfullargspec(self.func)[0][1:]

        if len(args) > len(args_name):
            args[len(args_name)-1] = " ".join(args[len(args_name)-1:])

            args = args[:len(args_name)]

        elif len(args) < len(args_name):
            raise Exception("Not enough arguments for {}, required arguments: {}"
                .format(self.comm, ", ".join(args_name)))

        ann = self.func.__annotations__

        for x in range(0, len(args_name)):
            v = args[x]
            k = args_name[x]

            if type(v) == ann[k]:
                pass

            else:
                try:
                    v = ann[k](v)

                except:
                    raise TypeError("Invalid type: got {}, {} expected"
                        .format(ann[k].__name__, v.__name__))

            args[x] = v

        if len(self.subcommands)>0:
            subcomm = args.pop(0)

            for s in self.subcommands:
                if subcomm == s.comm:
                    c = message.getBody().split(" ")
                    message.setBody(c[0] + " " + " ".join(c[2:]))

                    s.run(message)
                    break

        else:
            self.func(message, *args)



class SubCommand(Command):
    """ Subcommand class """
    def __init__(self, parent, comm, *, desc=""):
        self.comm = comm
        self.parent = parent
        self.layer = layer
        self.subcommands = []
        parent.subcommands.append(self)


class Bot:
    """ Bot instance, lame sync copy of my other lib martmists/asynctwitch """
    
    def __init__(self, prefix="!"):
        self.cache = []
        self.commands = {}
        self.layer = None
        
    def set_layer(self, layer):
        self.layer = layer

    def command(*args, **kwargs):
        """ Add a command """
        return Command(*args, **kwargs)
        
    def reload(self):
        """ TODO: Add a way to reload everything """
        raise UnimplementedError
        
    def parse_commands(self, message):
        """ Shitty command parser I made """
        content = message.getBody()
        
        if content.startswith(self.prefix):

            m = content[len(self.prefix):]
            cl = m.split(" ")
            w = cl.pop(0).lower().replace("\r","")
            m = " ".join(cl)

            if w in [command for command in self.commands if not command.unprefixed]:
                yield from self.commands[w].run(message)

        else:
            cl = content.split(" ")
            w = cl.pop(0).lower()

            if w in [command for command in self.commands if command.unprefixed]:
                yield from self.commands[w].run(message)