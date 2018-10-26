from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType

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
                # TODO
                pass
