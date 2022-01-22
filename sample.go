func (t testItem) evaluate(s string) *testOutput {
    result := &testOutput{}

    match, value, err := t.findValue(s)
    if err != nil {
        fmt.Fprintf(os.Stderr, err.Error())
        return failTestItem(err.Error())
    }

    if t.Set {
        if match && t.Compare.Op != "" {
            result.ExpectedResult, result.testResult = compareOp(t.Compare.Op, value, t.Compare.Value, t.value())
        } else {
            result.ExpectedResult = fmt.Sprintf("'%s' is present", t.value())
            result.testResult = match
        }
    } else {
        result.ExpectedResult = fmt.Sprintf("'%s' is not present", t.value())
        result.testResult = !match
    }

    result.flagFound = match
    var isExist = "exists"
    if !result.flagFound {
        isExist = "does not exist"
    }
    switch t.auditUsed {
    case "auditCommand":
        glog.V(3).Infof("Flag '%s' %s", t.Flag, isExist)
    case "auditConfig":
        glog.V(3).Infof("Path '%s' %s", t.Path, isExist)
    case "auditEnv":
        glog.V(3).Infof("Env '%s' %s", t.Env, isExist)
    default:
        glog.V(3).Infof("Error with identify audit used %s", t.auditUsed)
    }

    return result
}


func (t testItem) findValue(s string) (match bool, value string, err error) {
    if t.auditUsed == AuditEnv {
        et := envTestItem(t)
        return et.findValue(s)
    }

    if t.auditUsed == AuditConfig {
        pt := pathTestItem(t)
        return pt.findValue(s)
    }

    ft := flagTestItem(t)
    return ft.findValue(s)
}

func (t flagTestItem) findValue(s string) (match bool, value string, err error) {
    if s == "" || t.Flag == "" {
        return
    }
    match = strings.Contains(s, t.Flag)
    if match {
        // Expects flags in the form;
        // --flag=somevalue
        // flag: somevalue
        // --flag
        // somevalue
        // DOESN'T COVER - use pathTestItem implementation of findValue() for this
        // flag:
        //     - wehbook
        pttn := `(` + t.Flag + `)(=|: *)*([^\s]*) *`
        flagRe := regexp.MustCompile(pttn)
        vals := flagRe.FindStringSubmatch(s)

        if len(vals) > 0 {
            if vals[3] != "" {
                value = vals[3]
            } else {
                // --bool-flag
                if strings.HasPrefix(t.Flag, "--") {
                    value = "true"
                } else {
                    value = vals[1]
                }
            }
        } else {
            err = fmt.Errorf("invalid flag in testItem definition: %s", s)
        }
    }
    glog.V(3).Infof("In flagTestItem.findValue %s", value)

    return match, value, err
}


