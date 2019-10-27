import argparse
from typing import List, Tuple, Dict


class AssemblyException(Exception):
    pass

class CompileException(Exception):
    pass


class Command:
    def __init__(self) -> None:
        self.opcode = ""
        self.command = ""
        self.args : List[str] = []

    def __repr__(self) -> str:
        return "%s %s" % (self.command, self.args)

    cmdtbl = {
            "set":("31",2), "echon":("44",1), "echoc":("54",1),
            "input":("24",1), "jgz":("57",2), "pointer":("46",1),
            "exit":("88",0), "add":("781",2), "sub":("782",2),
            "mul":("788",2), "div":("787",2), "random":("83",1),
            "jmp":("31",1)
    }

    escapetbl = {
        "\\n":"\n", "\\t":"\t", "\\r":"\r", "\\b":"\b", '\\"':'"', "\\'":"'"
    }

    def parseFromLine(self, line: str) -> None:

        sp = []
        cur = ""
        for i in range(len(line)):
            if line[i] == ' ' or line[i] == '\t':
                sp.append(cur)
                cur = line[i+1:]
                break
            cur+=line[i]
        sp.append(cur)
        #sp = line.split(' ',1)
        #cmd, args = line.split(' ', 1)
        cmd = sp[0]
        if self.cmdtbl.get(cmd) == None:
            raise AssemblyException("No command found")
        info = self.cmdtbl.get(cmd)
        self.opcode = info[0]
        self.command = cmd
        if info[1] > 0:
            if len(sp) == 1:
                raise AssemblyException("Argument mismatch")
            self.args = self.parseArgs(sp[1])
            if len(self.args) != info[1]:
                raise AssemblyException("Argument mismatch")

        

    def parseArgs(self, line: str) -> List[int]:
        rawargs: List[str] = []
        inquote = False
        cur = ""
        for c in line:
            if (c == ' ' or c == '\t') and not inquote:
                continue
            if c == '"':
                inquote = not inquote
                cur += c
                continue
            if c == ',' and not inquote:
                rawargs.append(cur)
                cur = ""
                continue
            cur += c
        if inquote:
            raise AssemblyException("Argument parse error")
        rawargs.append(cur)

        return rawargs

    def toOpCode(self) -> str:
        o = self.opcode
        for a in self.args:
            n = self.convertArg(a)
            o += self.convertNum(n)
        return o

    def convertArg(self, arg: str) -> int:
        if arg.startswith("0x"):
            return int(arg,16)
        if arg.startswith('"'):
            s = arg[1:-1]
            if self.escapetbl.get(s) != None:
                s = self.escapetbl.get(s)
            return ord(s)
        try:
            return int(arg)
        except ValueError:
            return arg
        

    def convertNum(self, num: int) -> str:
        if num == 0:
            return "088"
        
        if num > 0:
            return oct(num)[2:] + "88"
        else:
            return oct(-num)[2:] + "87"


class Catssembler:
    def __init__(self) -> None:
        pass

    def removeComment(self, line: str) -> str:
        inquote = False
        for i in range(len(line)):
            if line[i] == '"':
                inquote = not inquote
            elif line[i] == '#':
                if not inquote:
                    return line[0:i]
        return line

    def parseCommands(self, code: str) -> Tuple[List[Command], Dict[str, int]]:
        cmds: List[Command] = []
        lines = code.splitlines()
        labels = {}

        for line in lines:
            line = self.removeComment(line)
            line = line.lstrip().rstrip()
            if line == '':
                continue


            if line[-1] == ':':
                labels[line[:-1]] = len(cmds)
                continue

            cmd = Command()
            cmd.parseFromLine(line)
            cmds.append(cmd)

        return (cmds, labels)


    def makeOpCode(self, code: List[Command], labels: Dict[str,int]) -> str:
        output = ""
        c: Command
        for c in code:
            
            if c.command == "jmp":
                if labels.get(c.args[0]) == None:
                    raise AssemblyException("Invalid label '{}'".format(c.args[0]))
                c.args = ['-1',str(labels[c.args[0]] - 1)]
            elif c.command == "jgz":
                if labels.get(c.args[1]) == None:
                    raise AssemblyException("Invalid label '{}'".format(c.args[1]))
                c.args[1] = str(labels[c.args[1]] - 1)
            
                
            output += c.toOpCode()
        return output

    def convert(self, opcode: str) -> str:
        output = ""
        i: str
        for i in opcode:
            output += chr(ord(i)-48+0x1f638)
        return output
        
    def assemble(self, code: str) -> str:
        commands, labels = self.parseCommands(code)
        return self.convert(self.makeOpCode(commands, labels))


class Macro:
    def __init__(self, args: str) -> None:
        self.args = args

    def parseArgs(self, line: str) -> List[int]:
        rawargs: List[str] = []
        inquote = False
        cur = ""
        for c in line:
            if (c == ' ' or c == '\t') and not inquote:
                continue
            if c == '"':
                inquote = not inquote
                cur += c
                continue
            if c == ',' and not inquote:
                rawargs.append(cur)
                cur = ""
                continue
            cur += c
        if inquote:
            raise AssemblyException("Argument parse error")
        rawargs.append(cur)

        return rawargs
    
    def process(self) -> str:
        return ""

    

class PrintMacro(Macro):
    escapetbl = {
        "\\n":"\n", "\\t":"\t", "\\r":"\r", "\\b":"\b", '\\"':'"', "\\'":"'"
    }
    def process(self) -> str:
        arg = self.args
        if arg[0] != '"' or arg[-1] != '"':
            raise CompileException("String literal error")
        raw = arg[1:-1]
        o=""
        i=0
        while i < len(raw):
            if raw[i:].startswith("\\"):
                nxt = raw[i:i+2]
                if self.escapetbl.get(nxt) == None:
                    raise CompileException("String escape error")
                o+=self.escapetbl.get(nxt)
                i+=2
                continue
            o+=raw[i]
            i+=1
        result = ""
        for c in o:
            result += "set -5, %d\n" % (ord(c))
            result += "echoc -5\n"
        return result

class MovMacro(Macro):
    def process(self) -> str:
        argv = self.parseArgs(self.args)
        result = "set {},{}\n".format(argv[0],argv[1])
        result+= "pointer {}\n".format(argv[0])
        
        return result

class AddMacro(Macro):
    def process(self) -> str:
        argv = self.parseArgs(self.args)
        if argv[1][0] != "$":
            return "add {},{}\n".format(argv[0],argv[1])
        result = "set -5,{}\n".format(argv[1][1:])
        result+= "add {},-5\n".format(argv[0])
        return result

class SubMacro(Macro):
    def process(self) -> str:
        argv = self.parseArgs(self.args)
        if argv[1][0] != "$":
            return "sub {},{}\n".format(argv[0],argv[1])
        result = "set -5,{}\n".format(argv[1][1:])
        result+= "sub {},-5\n".format(argv[0])
        return result

class MulMacro(Macro):
    def process(self) -> str:
        argv = self.parseArgs(self.args)
        if argv[1][0] != "$":
            return "mul {},{}\n".format(argv[0],argv[1])
        result = "set -5,{}\n".format(argv[1][1:])
        result+= "mul {},-5\n".format(argv[0])
        return result

class DivMacro(Macro):
    def process(self) -> str:
        argv = self.parseArgs(self.args)
        if argv[1][0] != "$":
            return "div {},{}\n".format(argv[0],argv[1])
        result = "set -5,{}\n".format(argv[1][1:])
        result+= "div {},-5\n".format(argv[0])
        return result


class IfMacro(Macro):
    def process(self) -> str:
        try:
            #argv = self.parseArgs(self.args)
            argv = self.args.split()
            #print(argv)
            
            opnd1 = argv[0]
            opnd2 = argv[2]
            comp = argv[1]
            tolabel = argv[4]

            result = ""
            if opnd1[0] == "$":
                result+= "set -5,{}\n".format(opnd1[1:])
            else:
                result+= "set -5,{}\n".format(opnd1)
                result+= "pointer -5\n"
            
            if opnd2[0] == "$":
                result+= "set -6,{}\n".format(opnd2[1:])
            else:
                result+= "set -6,{}\n".format(opnd2)
                result+= "pointer -6\n"

            if comp == "<":
                result+= "sub -6,-5\n"
                result+= "jgz -6,{}\n".format(tolabel)
            elif comp == ">":
                result+= "sub -5,-6\n"
                result+= "jgz -5,{}\n".format(tolabel)
            return result
        except:
            raise CompileException("Syntax error")



class Catpiler:
    def __init__(self) -> None:
        pass

    macrotbl = {
        "print":PrintMacro, "mov":MovMacro, 
        "add":AddMacro, "sub":SubMacro, "mul":MulMacro, "div":DivMacro,
        "if":IfMacro
    }

    def compile(self, code: str) -> str:
        newcode = ""
        lines = code.splitlines()
        linenumber = 0
        for line in lines:
            linenumber += 1
            line = self.removeComment(line)
            line = line.rstrip().lstrip()
            if line == '':
                continue
            try:
                cmds = self.parseLine(line)
                if self.macrotbl.get(cmds[0]) != None:
                    macrotype = self.macrotbl.get(cmds[0])
                    macro : Macro = macrotype(cmds[1])
                    newcode += macro.process()
                    continue
            except CompileException as e:
                errorExit("{}: {}".format(linenumber, e.args[0]))
                
            
            newcode+=line+"\n"
        return newcode

            
            

    def parseLine(self, line: str) -> Tuple[str,str]:
        cmds = []
        cur = ""
        for i in range(len(line)):
            if line[i] == ' ' or line[i] == '\t':
                return (line[0:i], line[i+1:])
        return (line, "")

    def removeComment(self, line: str) -> str:
        inquote = False
        for i in range(len(line)):
            if line[i] == '"':
                inquote = not inquote
            elif line[i] == '#':
                if not inquote:
                    return line[0:i]
        return line
    



def errorExit(msg: str) -> None:
    print("ERROR: " + msg)
    exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="input source code file")
    parser.add_argument("-s", "--onlycompile",action="store_true")
    parser.add_argument("-a", "--assemble", action="store_true")
    parser.add_argument("-o", "--output", type=str, help="path to output file")
    
    args = parser.parse_args()
    

    with open(args.input, 'r') as fp:
        content = fp.read()
        catasm = Catssembler()
        output = ""

        if args.onlycompile:
            catcom = Catpiler()
            output = catcom.compile(content)
        elif args.assemble:
            output = catasm.assemble(content)
        else:
            catcom = Catpiler()
            asmcode = catcom.compile(content)
            output = catasm.assemble(asmcode)


        if args.output == None:
            print(output)
        else:
            with open(args.output, 'w', encoding='utf-8') as wfp:
                wfp.write(str(output))
                print("Successfully compiled " + args.output)

