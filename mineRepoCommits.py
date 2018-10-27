from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType
import re

class Method:
    def __init__(self, method):
        self.signature = re.sub(r'\s+', ' ' ,' '.join(method[:-1]))
        self.name = method[4].strip()
        args = method[5][1:-1].strip()
        if args:
            self.args = set(list(map(lambda arg: arg.replace(']', '] ').split()[-1], args.split(','))))
        else:
            self.args = set()

    def hasLessArgsThan(self, other):
        return len(self.args & other.args) < len(other.args)
    
    def __str__(self):
        return self.signature
        return self.name + '(' + ', '.join(self.args) + ')'

    __repr__ = __str__

    def __eq__(self, other):
        return self.name == other.name

def isFirstOfChunkInfo(line):
    infoParts = line.strip().split('@@')
    if len(infoParts) == 3: # check if the format is correct
        return True
    return False

def getMethodDifferences(removedContent, addedContent):
    regex = r'\s*(public|private|protected)?(\s+static)?(\s+final)?\s+(\w+)\s+(\w+)\s*(\([^\)]*\))\s*(throws [^\{]*)?\{'
    oldMethods = sorted(list(map(lambda method: Method(method), re.findall(regex, removedContent))), key= lambda item: item.name)
    newMethods = sorted(list(map(lambda method: Method(method), re.findall(regex, addedContent))), key= lambda item: item.name)
    for oldMethod in oldMethods:
        for newMethod in newMethods:
            if oldMethod == newMethod and oldMethod.hasLessArgsThan(newMethod):
                print(str(oldMethod) + ' --> ' + str(newMethod))
                print()
                break

def readDiffToDetectChangedMethods(diff):
    removedContent = ''
    addedContent = ''
    processing = False
    modified = None
    for index, line in enumerate(diff.split('\n')):
        if isFirstOfChunkInfo(line): # it is chunk header
            if processing:
                processing = False
                if modified: # it has both removed and added lines
                    getMethodDifferences(removedContent, addedContent)
                modified = None
                removedContent = ''
                addedContent = ''
        else: # it is file content
            if line.startswith('-'):
                processing = True
                modified = False
                removedContent += ' ' + line[1:]
            elif line.startswith('+'):
                processing = True
                if modified == False:
                    modified = True
                addedContent += ' ' + line[1:]
            elif processing:
                processing = False
                if modified: # it has both removed and added lines
                    getMethodDifferences(removedContent, addedContent)
                modified = None
                removedContent = ''
                addedContent = ''

repo = '../repos/jdk7u-jdk' # repo path either local or remote
for commit in RepositoryMining(repo, only_modifications_with_file_types=['.java']).traverse_commits():
    for modification in commit.modifications:
        if modification.change_type != ModificationType.ADD and modification.change_type != ModificationType.DELETE and modification.added > 0 and modification.removed > 0:
            needsAssess = False
            for method in modification.methods:
                if len(method.parameters) > 0:
                    needsAssess = True
                    break
            if needsAssess: # file may have "added paramerer methods" 
                readDiffToDetectChangedMethods(modification.diff)
