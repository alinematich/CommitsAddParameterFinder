from pydriller import RepositoryMining
from pydriller.domain.commit import ModificationType

repo = '../repos/jdk7u-jdk'
for commit in RepositoryMining(repo, only_modifications_with_file_types=['.java']).traverse_commits():
    for mod in commit.modifications:
        if mod.change_type != ModificationType.ADD and mod.change_type != ModificationType.DELETE and mod.added > 0 and mod.removed > 0 and len(mod.methods) > 0:
            pass
    break