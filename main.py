import csv
from parseYaml import checks, parsed_yaml_file
import re
import glob
import yaml

f = open('output.csv', 'w')
writer = csv.writer(f)
f_ch5_test = open('ch5_test.txt', 'w')

def loadAllTest():
    yamlList = []
    for file in sorted(glob.glob('./cis_1_20/*.yaml')):
    #for file in glob.glob('./*.yaml'):
        file = open(file)
        file = yaml.load(file, Loader=yaml.FullLoader)
        yamlList.append(file)
    #print(yamlList[0])
    return yamlList

def runTest(bm):
    yf = parsed_yaml_file(bm)
    for k in range(yf.getMaxId()):
        for i in range(yf.getMaxSubId(k)):
            yf.check = checks(k,i,bm)
            #print(yf.check.execute(),yf.check.id, yf.check.text)
            writer.writerow([yf.check.execute(),yf.check.id, yf.check.text])

def main():
    benchMarks = loadAllTest()
    for i in range(len(benchMarks)):
        runTest(benchMarks[i])

    ch5_yaml = open('./ch5_policies_specific.yaml')
    ch5_yaml = yaml.load(ch5_yaml, Loader=yaml.FullLoader)
    yf = parsed_yaml_file(ch5_yaml)
    for k in range(yf.getMaxId()):
        for i in range(yf.getMaxSubId(k)):
            yf.check = checks(k,i,ch5_yaml)
            f_ch5_test.writelines([yf.check.id+"\n",yf.check.text+"\n"])
            f_ch5_test.write("===Audit Result===\n")
            f_ch5_test.writelines(yf.check.line)
            f_ch5_test.write("===Audit Result===\n\n")


if __name__ == "__main__":
    main()
