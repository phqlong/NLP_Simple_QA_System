
stdCityName = {
    'HỒ CHÍ MINH': 'HCMC',
    'HÀ NỘI': 'HN',
    'ĐÀ NẴNG': 'DANANG',
    'NHA TRANG': 'NTRANG',
    'HUẾ': 'HUE',
}


class Pattern:
    def __init__(self, typ, name=None, val=None, queryType=None):
        self.type = typ
        self.name = name
        self.val = val
        self.queryType = queryType

    def __str__(self):
        if self.type == 'WH':
            return f'({self.type}-{self.queryType} {self.name})'
        elif self.type == "YN":
            return f'({self.type})'
        elif self.type in ['TRAIN-NAME', 'CITY-NAME', 'TIMEMOD']:
            return f'({self.type} {self.name} "{self.val}")'
        else:
            return f'({self.name} {self.type} {self.val})'

    def logicalForm(self):
        if self.type == "WH":
            return f'{self.type} {self.name}'
        elif self.type == "YN":
            return f'{self.type}'
        elif self.type == "PRED":
            return f'("{self.val}" {self.name})'
        elif self.type == "LSUBJ":
            return f'(AGENT {self.name} {self.val})'
        else:
            return f'({self.type} {self.name} {self.val})'


class GrammaticalRelations:
    def __init__(self, relationSet):
        self.relationSet = relationSet
        self.patterns = []
        self.queryPatterns = []
        self.context = {
            'pred': None,
            'fromLoc': False,
            'toLoc': False,
        }
        self.var = {
            'TRAIN': '?t',
            'DCITY': '?dc',
            'ACITY': '?ac',
            'DTIME': '?dt',
            'ATIME': '?at',
            'RUNTIME': '?rt',
        }

    def append_PRED(self):
        rootRels = [rel for rel in self.relationSet if rel.rule == 'ROOT']

        for rel in rootRels:
            pred = Pattern('PRED', 'v1', rel.tail.upper())
            self.patterns.append(pred)
            self.context['pred'] = 'v1'

    def append_FROM_LOC(self):
        rels = [rel for rel in self.relationSet if rel.rule == 'case-d']

        for rel in rels:
            cityName = stdCityName[rel.head.upper()]

            cityLit = Pattern('CITY-NAME', 'c1', cityName)
            fromLoc = Pattern('FROM-LOC', self.context['pred'], cityLit)

            self.patterns.append(fromLoc)
            self.context['fromLoc'] = True
            self.var['DCITY'] = cityName

    def append_TO_LOC(self):
        rels = [rel for rel in self.relationSet if rel.rule in
                ['case-a', 'dobj-a']]

        for rel in rels:
            cityName = rel.tail.upper() if rel.rule == 'dobj-a' else rel.head.upper()
            cityName = stdCityName[cityName]

            cityLit = Pattern('CITY-NAME', 'c2', cityName)
            toLoc = Pattern('TO-LOC', self.context['pred'], cityLit)

            self.patterns.append(toLoc)
            self.context['toLoc'] = True
            self.var['ACITY'] = cityName

    def append_LSUBJ(self):
        # Tàu hỏa - nào
        rels = [rel for rel in self.relationSet if rel.rule == 'det-wh']

        for rel in rels:
            whquery = Pattern('WH', queryType='TRAIN', name='t1')
            self.queryPatterns.append(whquery)

            lsubj = Pattern('LSUBJ', self.context['pred'], 't1')
            self.patterns.append(lsubj)

        # Tàu hỏa - B3
        rels = [rel for rel in self.relationSet if rel.rule == 'namemod']

        for rel in rels:
            trainName = rel.tail.upper()
            trainLit = Pattern('TRAIN-NAME', 't1', trainName)
            lsubj = Pattern('LSUBJ', self.context['pred'], trainLit)

            self.patterns.append(lsubj)
            self.var['TRAIN'] = trainName

    def append_TIMEMOD(self):
        rels = [rel for rel in self.relationSet if rel.rule in ['case-t', 'case-t-wh', 'is']]

        if self.context['fromLoc'] and self.context['toLoc']:
            typ, var, name = ('RUN-IN', 'RUNTIME', 'r1')
        elif self.context['fromLoc']:
            typ, var, name = ('DEPART-AT', 'DTIME', 'd1')
        elif self.context['toLoc']:
            typ, var, name = ('ARRIVE-AT', 'ATIME', 'a1')

        for rel in rels:
            # Lúc 19:00HR => case-t
            if rel.rule == 'case-t':
                time = rel.head.upper()
                timemod = Pattern('TIMEMOD', name, time)
                pat = Pattern(typ, self.context['pred'], timemod)
                
                self.patterns.append(pat)
                self.var[var] = time

            # mấy giờ? => 'case-t-wh' | 'is'
            else:
                whquery = Pattern('WH', queryType=var, name=name)
                self.queryPatterns.append(whquery)

                pat = Pattern(typ, self.context['pred'], val=name)
                self.patterns.append(pat)

    def append_YN(self):
        ynRels = [rel for rel in self.relationSet if rel.rule == 'advmod']

        if ynRels:
            ynquery = Pattern('YN')
            self.queryPatterns.append(ynquery)

    def getGramRel(self):
        self.append_PRED()
        self.append_LSUBJ()
        self.append_FROM_LOC()
        self.append_TO_LOC()
        self.append_TIMEMOD()
        self.append_YN()

        return self.queryPatterns + self.patterns

    def getLogicalForms(self):
        def convert2lf(p): 
            return p.logicalForm()
        
        queries = ' '.join(map(convert2lf, self.queryPatterns))
        attribs = ' '.join(map(convert2lf, self.patterns))

        return f'({queries}: {attribs})'
