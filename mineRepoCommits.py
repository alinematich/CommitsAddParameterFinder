from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType
import javalang

class Parameter:
    def __init__(self, parameter):
        self.name = parameter.name
        self.type = parameter.type.name + '[]' * len(parameter.type.dimensions)

    def __str__(self):
        return self.type + ' ' + self.name

    __repr__ = __str__

    def __eq__(self, other):
        return self.name == other.name

class Method:
    def __init__(self, method, path):
        self.name = method.name
        if path:
            self.name = '::'.join(path) + '::' + method.name
        self.parameters = map(Parameter, method.parameters)
        return_type = 'void'
        if method.return_type:
            return_type = method.return_type.name + '[]' * len(method.return_type.dimensions)
        modifiers = ' '.join(list(method.modifiers))
        if modifiers:
            modifiers += ' '
        self.signature =  modifiers + return_type + ' ' + self.name + '(' + ', '.join(map(str, self.parameters)) + ')'
    
    def __str__(self):
        return self.signature

    __repr__ = __str__

    def __eq__(self, other):
        return self.name == other.name

def getFirstOfChunkInfo(line):
    infoParts = line.strip().split('@@')
    if len(infoParts) == 3 and line.startswith('@@'): # check if the format is correct
        linesInfo = infoParts[1].split() 
        linesInfo = linesInfo[0].split(',') + linesInfo[1].split(',')
        linesInfo[0] = int(linesInfo[0][1:]) - 1
        linesInfo[1] = int(linesInfo[1])
        linesInfo[2] = int(linesInfo[2][1:]) - 1
        linesInfo[3] = int(linesInfo[3]) # by format: [old first line, old line count, new first line, new line count]
        return linesInfo
    return None

def getOldDocFromDiff(newDoc, diff):
    oldDoc = []
    newDoc = newDoc.split('\n')
    diff = diff.split('\n')
    lineNum = 0
    for index, line in enumerate(diff):
        chunkHeader = getFirstOfChunkInfo(line)
        if chunkHeader: # it is chunk header
            oldDoc += newDoc[lineNum : chunkHeader[2]]
            lineNum = chunkHeader[2]
        else: # it is file content
            if line.startswith('-'):
                oldDoc.append(line[1:])
            elif line.startswith('+'):
                lineNum += 1
            else:
                oldDoc.append(newDoc[lineNum])
                lineNum += 1
    oldDoc += newDoc[lineNum:]
    return '\n'.join(oldDoc)

# constructor declaration

def parseMethods(code):
    tree = javalang.parse.parse(code)
    methods = []
    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        methods.append(Method(node, map(lambda node: node.name, filter(lambda node: hasattr(node, 'name'), path))))
    return sorted(methods, key= lambda item: item.name)

repo = '../repos/jdk7u-jdk' # repo path either local or remote
for commit in RepositoryMining(repo, only_modifications_with_file_types=['.java']).traverse_commits():
    for modification in commit.modifications:
        if modification.filename.endswith('.java') and modification.change_type != ModificationType.ADD and modification.change_type != ModificationType.DELETE and modification.added > 0 and modification.removed > 0:
            needsAssess = False
            for method in modification.methods:
                if method.parameters:
                    needsAssess = True
                    break
            if needsAssess: # file may have "added paramerer methods"
                newDoc = modification.source_code
                oldDoc = getOldDocFromDiff(newDoc, modification.diff)
                oldMethods = parseMethods(oldDoc)
                newMethods = parseMethods(newDoc)
                for oldMethod in oldMethods:
                    for newMethod in newMethods:
                        if oldMethod == newMethod:
                            print(oldMethod)
                            print()
                            print(newMethod)
                            print('------------################---------------')
                            break


