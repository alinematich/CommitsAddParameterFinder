# CommitsAddParameterFinder
Finds all the Git commits that add a parameter to a method in Java files.

## Installation
Install python3
```sh
$ sudo apt-get update
$ sudo apt-get install python3.6
```

Install pydriller

```sh
$ pip install pydriller
```
pydriller package: https://github.com/ishepard/pydriller


Install javalang

```sh
$ pip install javalang
```
javalang package: https://github.com/c2nes/javalang

## Usage

```sh
$ python3 mineRepoCommits.py
```

## Tests

This code is already ran on these two repositories:

Repository: https://github.com/TheAlgorithms/Java

Result: https://github.com/alinematich/CommitsAddParameterFinder/blob/master/results/Java-Results.csv

Repository: https://github.com/iluwatar/java-design-patterns

Result: https://github.com/alinematich/CommitsAddParameterFinder/blob/master/results/java-design-patterns-Results.csv
