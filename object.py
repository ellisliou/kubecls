from contextlib import nullcontext
from curses.ascii import NUL
import yaml
import re
import strconv
from parseYaml import parsed_yaml_file
a_yaml_file = open("master.yaml")

parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
ch = parsed_yaml_file["groups"]

def failTestItem(line):
    x = testOutput()
    x.testResult = False
    x.actualResult = line
    return x 

class compare:
    def __init__(self, op = None, value = None) -> None:
        if op == None and value == None:
            self.op = ""
            self.value = ""

        else:
            self.op = op
            self.value = value

class testOutput:
    def __init__(self) -> None:
        self.testResult = None #bool
        self.flagFound = None  #bool
        self.actualResult = ""
        self.expectedResult = ""   

    def failTestItem(self,s):
        self.testResult = False
        self.actualResult = s
        return self

class testItem:
    def __init__(self, id, sub_id, item_number,line):
        if "use_multiple_values" in ch[id]["checks"][sub_id]:
            self.isMultipleOutput = ch[id]["checks"][sub_id]["use_multiple_values"]
        else:
            self.isMultipleOutput = False
        
        self.item =  ch[id]["checks"][sub_id]["tests"]["test_items"][item_number]
        self.id = ch[id]["checks"][sub_id]["id"]
        self.line = line
        if "set" in self.item:
            self.set = self.item["set"]
        else:
            self.set = True
        if "env" in self.item:
            self.auditUsed = "env"
            self.test = envTestItem(id, sub_id, item_number, line)

        elif "flag" in self.item:
            self.test = flagTestItem(self.item)
            self.auditUsed = "flag"
    
    def execute(self):
        result = testOutput()
        output = []
        if self.isMultipleOutput:
            output =  [item.strip() for item in self.line]
        else:
            output.insert(0,self.line[0])
        
        for op in range(len (output)):
            result = self.evaluate(output[op])
            if not result.testResult:
                break
        
        result.actualResult = self.line
        return result
    
    
    def evaluate(self, line):
        result = testOutput()
        match, value, err = self.test.findValue(line)
        if err != None:
            return failTestItem("err")
        if  self.set:
            if match and self.test.comp.op != "":
                result.expectedResult, result.testResult = compareOp(self.test.comp.op,value,self.test.comp.value)
            
            else:
                result.expectedResult = "test1"
                result.testResult = match

        else:
            result.expectedResult = "test2"
            result.testResult = not match
        result.flagFound = match
        return result

def compareOp(tCompareOp, flagVal, tCompareValue):
    expectedResultPattern = ""
    testResult = False
    
    if  tCompareOp == "eq":
        value = flagVal.lower()
        if value == "false" or value == "true":
            testResult = value == tCompareValue

        else:
            testResult = flagVal == tCompareValue

    elif tCompareOp == "noteq":
        value = flagVal.lower()
        if value == "false" or value == "true":
            testResult = value == tCompareValue

        else:
            testResult = not (flagVal == tCompareValue)
    
    elif tCompareOp == "gte" or tCompareOp == "gt" or tCompareOp == "lt" or  tCompareOp == "lte":
        tCompareValue = str(tCompareValue)
        a, b, err = toNumeric(flagVal, tCompareValue)
        if err != None:
            expectedResultPattern = "Invalid Number"
            return expectedResultPattern, False

        if tCompareOp == "gt":
            expectedResultPattern = "is greater than"
            testResult = a > b

        elif tCompareOp == "gte":
            expectedResultPattern = "is greater or equal to"
            testResult = a > b

        elif tCompareOp == "lt":
            expectedResultPattern = "is lower than"
            testResult = a < b

        elif tCompareOp == "lte":
            expectedResultPattern = "is lower than or equal to"
            testResult = a <= b   

    elif tCompareOp == "has":
        expectedResultPattern = "has"
        testResult = tCompareValue in flagVal

    elif tCompareOp == "nothave":
        expectedResultPattern = "is lower than or equal to"
        testResult = not(tCompareValue in flagVal)

    elif tCompareOp == "regex":
        expectedResultPattern = " matched by regex expression "
        opRe = re.compile(tCompareValue)
        testResult = opRe.match(flagVal)

    elif tCompareOp == "valid_elements":
        expectedResultPattern = "contains valid element"
        s = splitAndRemoveLastSeparator(flagVal, ",")
        target = splitAndRemoveLastSeparator(tCompareValue, ",")
        testResult = allElementValid(s,target)
    elif tCompareOp == "bitmask":
        requested = int(flagVal,8)
        inputVal = int(tCompareValue,8)
        testResult = (requested & inputVal) == requested

    if expectedResultPattern == "":
        return expectedResultPattern, testResult
    return "testResult",testResult

def toNumeric(a,b):
    c = strconv.convert_int(a.strip())
    d = strconv.convert_int(b.strip())
    err = None
    return c, d, err

def splitAndRemoveLastSeparator(s, sep):
    cleanS = s.strip().rstrip(sep)
    if len(cleanS) == 0:
        return []
    ts = cleanS.split(sep)
    for i in range (len(ts)):
        ts[i] = ts[i].strip()
    return ts

def allElementValid(s,t):
    sourceEmpty = len(s) == 0
    targetEmpty = len(s) == 0
    if sourceEmpty and targetEmpty:
        return True
    
    if (sourceEmpty or targetEmpty) and not(sourceEmpty and targetEmpty):
        return False
    
    for i in range(len(s)):
        found = False
        for k in range(len(t)):
            if s[i] == t[k]:
                found = True
                break
        if not found:
            return False
    return True



class flagTestItem(testItem):
    def __init__(self, item) -> None:
        self.flag =  item["flag"]
        if "compare" in item:
            self.comp = compare(item["compare"]["op"],item["compare"]["value"])
        else:
            self.comp = compare()
    def findValue(self, line):
        if line == "" or self.flag == "":
            match = False
            value = ""
            err = None
            return match, value, err
        match = self.flag in line
        pttn = '(' + self.flag + ')(=|: *)*([^\s]*) *'
        flagRe = re.compile(pttn)
        vals = flagRe.search(line)
        err = None
        value = None
        if vals != None:
            if vals[3] != "":
                value = vals[3]
            else:
                if self.flag.startswith("--"):
                    value = "true"
                else:
                    value = vals[1]
        else:
            err = "invalid flag in testItem definition"
        return match, value, err

class envTestItem(testItem):
    def __init__(self, item) -> None:
        self.flag = item["flag"]
        self.env = item["env"]
        if "compare" in item:
            self.comp = compare(item["compare"]["op"],item["compare"]["value"])
    
    def findValue(self, line, match, value, error):
        if line != "" and self.env != "":
            pttn = self.flag + '=.*(?:$|\\n)'
            r = re.compile(pttn)
            out = r.search(line)
            out = out.replace(out, "\n", "", 1)
            out = out.replace(out, "{self.flag}=", "", 1)
        
            if out != None:
                match = True
                value = out
            else:
                match = False
                value = ""
        
        err = None
        return match, value, err