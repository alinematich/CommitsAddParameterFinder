from pydriller import RepositoryMining

repo = '../repos/jdk7u-jdk'
for commit in RepositoryMining(repo, only_modifications_with_file_types=['.java']).traverse_commits():
    for mod in commit.modifications:
        if len(mod.methods) > 0:
            print(mod.methods[0].name, mod.methods[0].parameters)
    break