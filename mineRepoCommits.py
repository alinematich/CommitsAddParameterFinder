from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType

def getFirstOfChunkInfo(line):
    infoParts = line.strip().split('@@')
    if len(infoParts) == 3: # check if the format is correct
        className = None
        if ' class ' in infoParts[2]: # get class name if available
            headerWords = infoParts[2].split()
            className = headerWords[headerWords.index('class') + 1]
        linesInfo = infoParts[1].split() 
        linesInfo = linesInfo[0].split(',') + linesInfo[1].split(',')
        linesInfo[0] = linesInfo[0][1:]
        linesInfo[2] = linesInfo[2][1:] # by format: [old first line, old line count, new first line, new line count]
        return (linesInfo, className)
    return None

def readDiffToDetectChangedMethods(diff):
    for index, line in enumerate(diff.split('\n')):
        chunkInfo = getFirstOfChunkInfo(line)
        if chunkInfo:
            print(chunkInfo)

repo = '../repos/jdk7u-jdk'
for commit in RepositoryMining(repo, only_modifications_with_file_types=['.java']).traverse_commits():
    for modification in commit.modifications:
        if modification.change_type != ModificationType.ADD and modification.change_type != ModificationType.DELETE and modification.added > 0 and modification.removed > 0:
            needsAssess = False
            for method in modification.methods:
                if len(method.parameters) > 0:
                    needsAssess = True
                    break
            if needsAssess:
                readDiffToDetectChangedMethods(modification.diff)
                pass
