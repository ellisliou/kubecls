import csv
from parseYaml import checks, parsed_yaml_file
import re
import glob
import yaml

def loadAllTest():
    yamlList = []
    for file in glob.glob('./cis_1_20/*.yaml'):
    #for file in glob.glob('./*.yaml'):
        file = open(file)
        file = yaml.load(file, Loader=yaml.FullLoader)
        yamlList.append(file)
    return yamlList

def runTest(bm):
    yf = parsed_yaml_file(bm)
    for k in range(yf.getMaxId()):
        for i in range(yf.getMaxSubId(k)):
            yf.check = checks(k,i,bm)
            print(yf.check.execute(),yf.check.id, yf.check.text)

def main():
    benchMarks = loadAllTest()
    for i in range(len(benchMarks)):
        runTest(benchMarks[i])

if __name__ == "__main__":
    main()
