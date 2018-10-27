from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType
import re
import javalang

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
    chunkInfo = None
    lineNum = 0
    for index, line in enumerate(diff):
        info = getFirstOfChunkInfo(line)
        if info: # it is chunk header
            chunkInfo = (index, info)
            oldDoc += newDoc[lineNum : info[2]]
            lineNum = info[2]
        else: # it is file content
            if line.startswith('-'):
                oldDoc.append(line[1:])
            elif line.startswith('+'):
                lineNum += 1
            else:
                try: 
                    oldDoc.append(newDoc[lineNum])
                except:
                    break
                lineNum += 1
    return '\n'.join(oldDoc)

# constructor declaration

def parse(code, filename):
    tree = javalang.parse.parse(code)
    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        if node.parameters:
            print(node)
            print()
            print(filename)
            print()
            print(node.modifiers)
            print()
            if node.return_type:
                print(node.return_type.name)
                print()
            print(node.name)
            print()
            print(node.parameters)
            print("-----------------------#######################-----------------------")

repo = '../repos/jdk7u-jdk' # repo path either local or remote
for commit in RepositoryMining(repo, only_modifications_with_file_types=['.java']).traverse_commits():
    for modification in commit.modifications:
        if modification.change_type != ModificationType.ADD and modification.change_type != ModificationType.DELETE and modification.added > 0 and modification.removed > 0:
            needsAssess = False
            for method in modification.methods:
                if method.parameters:
                    needsAssess = True
                    break
            if needsAssess: # file may have "added paramerer methods"
                newDoc = modification.source_code
                oldDoc = getOldDocFromDiff(newDoc, modification.diff)
                parse(newDoc, modification.new_path)
