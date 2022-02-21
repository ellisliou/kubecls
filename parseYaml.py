import strconv
import re
from connect import *
class parsed_yaml_file:
    def __init__(self,yf):
        self.yaml = yf["groups"]
        self.check = None
    def getMaxId(self):
        return len(self.yaml)

    def getMaxSubId(self,id):
        return len(self.yaml[id]["checks"])

    def checks(self, id, sub_id):
        return self.yaml[id]["checks"][sub_id]

class checks(parsed_yaml_file):
    def __init__(self, id ,sub_id ,yf):
        super().__init__(yf)
        self.it = self.yaml[id]["checks"][sub_id]
        self.id = self.it["id"]
        self.text = self.it["text"]
        self.scored = self.it["scored"]
    
        if "tests" in self.it:
            self.tests = self.it["tests"]
            self.audit = self.it["audit"]
            self.line = runAudit(self.id,self.audit)
            self.type = "default"

            if "bin_op" in self.tests:
                self.binOp = self.tests["bin_op"]
                self.testItem = []
                for item in range(len(self.tests["test_items"])):
                    self.testItem.insert(item,testItem(self.it, id, sub_id, item, self.line))
            else:
                self.binOp = ""
                self.testItem = []
                self.testItem.insert(0,testItem(self.it, id, sub_id, 0, self.line))
        else:
            if "audit" in self.it:
                self.audit = self.it["audit"]
                self.line = runAudit(self.id,self.audit)
            self.type = "manual"
        
        if "audit_config" in self.it:
            self.auditConfig = self.it["audit_config"]
        else:
            self.auditConfig = ""


    def execute(self):
        result = []
        expectedResultArr = []
        if self.type == "manual":
            return "MANUAL"
        for i in range(len(self.testItem)):
            sub_result = self.testItem[i].execute()
            if (not sub_result.flagFound) and (self.auditConfig != ""):
                self.testItem[i].auditUsed = "AuditConfig"
                sub_result = self.testItem[i].execute()
            if (not sub_result.flagFound) and (self.testItem[i].env != ""):
                self.testItem[i].auditUsed = "AuditEnv"
                sub_result = self.testItem[i].execute()
            result.insert(i,sub_result)
            expectedResultArr.insert(i,sub_result.expectedResult)
        if self.binOp == "and" or self.binOp == "":
            totalResult = True
            for i in range(len(result)):
                totalResult = totalResult and result[i].testResult
        else:
            totalResult = False
            for i in range(len(result)):
                totalResult = totalResult or result[i].testResult
        if self.scored == True:
            if not totalResult:
                return "FAIL"
            else:
                return "PASS"
        else:
            if not totalResult:
                return "WARN"
            else:
                return "PASS"           

def failTestItem(line):
    x = testOutput()
    x.testResult = False
    x.actualResult = line
    return x 

class compare:
    def __init__(self, op = None, value = None):
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

class testItem():
    def __init__(self, it, id, sub_id, item_number,line):
        if "use_multiple_values" in it:
            self.isMultipleOutput = it["use_multiple_values"]
        else:
            self.isMultipleOutput = False
        
        self.item =  it["tests"]["test_items"][item_number]
        self.line = line
        self.auditUsed = "AuditCommand"
        
        if "set" in self.item:
            self.set = self.item["set"]
        else:
            self.set = True
        
        if "env" in self.item:
            self.env = "env"
        else:
            self.env = ""
        '''
        elif "flag" in self.item:
            self.test = flagTestItem(self.item)
            self.auditUsed = "flag"
        '''

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
        match, value, err = self.findValue(line)
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
    
    def findValue(self, s):
        if self.auditUsed == "AuditEnv":
            self.test = envTestItem(self.item)
            self.test.findValue(s)
        '''
        if self.auditUsed == "AuditConfig":
            self.test = pathTestItem(t)
            return self.test.findValue(s)
        '''
        self.test = flagTestItem(self.item)
        return self.test.findValue(s)

def compareOp(tCompareOp, flagVal, tCompareValue):
    expectedResultPattern = ""
    testResult = False
    if  tCompareOp == "eq":
        value = flagVal.lower()
        if value == "false" or value == "true":
            testResult = value == tCompareValue

        else:
            tCompareValue = str(tCompareValue)
            testResult = flagVal == tCompareValue

    elif tCompareOp == "noteq":
        tCompareValue = str(tCompareValue).lower()
        value = flagVal.lower()
        if value == "false" or value == "true":
            testResult = value != tCompareValue

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
        value = ""
        err = None
        if line == "" or self.flag == "":
            match = False
            value = ""
            err = None
            return match, value, err
        match = self.flag in line
        if match:
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
    
    def findValue(self, line):
        err = None
        if line != "" and self.env != "":
            pttn = self.env + '=.*(?:$|\\n)'
            r = re.compile(pttn)
            out = r.search(line)
            #print("test:",r,"\n",line)
            #out = out.replace(out, "\n", "", 1)
            #out = out.replace(out, "{self.flag}=", "", 1)
        
            if out != None:
                match = True
                value = out
                out = out.replace(out, "\n", "", 1)
                out = out.replace(out, "{self.flag}=", "", 1)
        
            else:
                match = False
                value = ""
        else:
            print("fault")
            err = "invalid flag in testItem definition"
            match = None
            value = ""
        return match, value, err

class pathTestItem(testItem):
    def __init__(self,item):
        self.flag = item["flag"]
        self.path = item["path"]
        if "compare" in item:
            self.comp = compare(item["compare"]["op"],item["compare"]["value"])
        else:
            self.comp = compare()

    def findValue(self, s):
        return None