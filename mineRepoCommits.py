from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType
import re

class Method:
    def __init__(self, name, args):
        self.name = name
        self.args = set(list(map(lambda arg: arg.replace('final', '').strip(), args)))

    def hasLessArgsThan(self, other):
        return len(self.args & other.args) < len(other.args)
    
    def __str__(self):
        return self.name + '(' + ', '.join(self.args) + ')'

    __repr__ = __str__

    def __eq__(self, other):
        return self.name == other.name

def getFirstOfChunkInfo(line):
    infoParts = line.strip().split('@@')
    if len(infoParts) == 3: # check if the format is correct
        className = None
        if ' class ' in infoParts[2]: # get class name if available
            headerWords = infoParts[2].split()
            className = headerWords[headerWords.index('class') + 1]
        linesInfo = infoParts[1].split() 
        linesInfo = linesInfo[0].split(',') + linesInfo[1].split(',')
        linesInfo[0] = int(linesInfo[0][1:])
        linesInfo[1] = int(linesInfo[1])
        linesInfo[2] = int(linesInfo[2][1:])
        linesInfo[3] = int(linesInfo[3]) # by format: [old first line, old line count, new first line, new line count]
        return (linesInfo, className)
    return None

def getMethodDifferences(removedContent, addedContent):
    regex = r'\s*(public|private|protected)?(\s+static)?(\s+final)?\s+(\w+)\s+(\w+)\s*\(([^\)]+)\)\s*(throws [^\{]*)?\{'
    oldMethods = sorted(list(map(lambda method: Method(method[4].strip(), method[5].split(',')), re.findall(regex, removedContent))), key= lambda item: item.name)
    newMethods = sorted(list(map(lambda method: Method(method[4].strip(), method[5].split(',')), re.findall(regex, addedContent))), key= lambda item: item.name)
    for oldMethod in oldMethods:
        for newMethod in newMethods:
            if oldMethod == newMethod and oldMethod.hasLessArgsThan(newMethod):
                print(str(oldMethod) + ' --> ' + str(newMethod))
                print()

def readDiffToDetectChangedMethods(diff):
    chunkInfo = None
    removedContent = ''
    addedContent = ''
    processing = False
    modified = None
    for index, line in enumerate(diff.split('\n')):
        tempInfo = getFirstOfChunkInfo(line)
        if tempInfo: # it is chunk header
            chunkInfo = tempInfo
            if processing:
                processing = False
                if modified:
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
                if modified:
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
