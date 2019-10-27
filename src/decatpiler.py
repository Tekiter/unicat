import sys
from unicat import *


class CalcCommandDump(CalcCommand):
    def __init__(self, args, size, func):
        self.args = args
        self.size = size
        self.type = ""
        if func(6, 3) == 9:
            self.type = "add"
        elif func(6, 3) == 3:
            self.type = "sub"
        elif func(6, 3) == 18:
            self.type = "mul"
        elif func(6, 3) == 2:
            self.type = "div"

    def __repr__(self):
        return "%s_%s(%s)" % ("CalcCommand", self.type, str(self.args)[1:-1])


def decompile(code: str) -> List[Command]:
    code = preprocess(raw)

    cf = CommandFetcher(code)
    pos=0
    cmds: List[Command] = []
    while not cf.isend(pos):
        cmd = cf.next(pos)
        pos += cmd.size()
        if isinstance(cmd, CalcCommand):
            cmd = CalcCommandDump(cmd.args, cmd.size, cmd.func)
        cmds.append(cmd)

    return cmds



if len(sys.argv) != 2:
    print("Usage: {} FILENAME".format(sys.argv[0]))
    exit(1)


filename = sys.argv[1]

with open(sys.argv[1], 'rb') as fp:
    data = fp.read()
    raw = data.decode("utf-8")

try:
    cmds = decompile(raw)
except:
    print("Decatpile failed")
    exit(1)


output = ""
for i in range(len(cmds)):
    output+= "{}\t {}\n".format(i+1, str(cmds[i]))
print(output)