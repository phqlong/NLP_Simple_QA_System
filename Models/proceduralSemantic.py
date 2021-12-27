from abc import ABC

class Proc(ABC):
    pass


class Procedure(Proc):
    def __init__(self, name, var=None):
        self.name = name
        self.var = var

    def __str__(self):
        if self.name == 'PRINT-ALL':
            return f'{self.name} {self.var}' 
        else:   
            # 'WH-...'
            return self.name


class Literal(Proc):
    def __init__(self, name, var=None):
        self.name = name
        self.var = var
        self.t = var['TRAIN']
        self.dc = var['DCITY']
        self.ac = var['ACITY']
        self.dt = var['DTIME']
        self.at = var['ATIME']
        self.rt = var['RUNTIME']

    def __str__(self):
        if self.name == 'TRAIN':
            return f'(TRAIN {self.t})'
        elif self.name == 'ATIME':
            return f'(ATIME {self.t} {self.ac} {self.at})'
        elif self.name == 'DTIME':
            return f'(DTIME {self.t} {self.dc} {self.dt})'
        else:   # RUN-TIME
            return f'(RUN-TIME {self.t} {self.dc} {self.ac} {self.rt})'


class ProceduralSemantic:
    def __init__(self, queryPatterns, var):
        self.queryPatterns = queryPatterns
        self.var = var
        self.procSemantics = []

    def getProcedure(self):
        literals = [Literal(lit, self.var)
                    for lit in ['TRAIN', 'ATIME', 'DTIME', 'RUN-TIME']]

        for q in self.queryPatterns:
            if q.type == 'WH':
                queryProc = Procedure('PRINT-ALL', self.var[q.queryType])
            else:
                queryProc = Procedure('CHECK-ALL-TRUE')
            self.procSemantics.append([queryProc] + literals)

        return [f"({' '.join(map(str, ps))})" for ps in self.procSemantics]

    def fetchDatabase(self, db_path):
        db = {
            'TRAIN': [],
            'ATIME': [],
            'DTIME': [],
            'RUN-TIME': [],
        }

        with open(db_path, 'r') as f:
            for row in f.readlines():
                data = tuple(row[1:-2].split(' '))  # Remove ( ) and split
                db[data[0]].append(data)

        return db

    def retrieve(self, procedure, database):
        def retrieveTable(table, varList):
            newTable = []
            for data in table:
                for i, var in enumerate(varList):
                    if '?' not in var and data[i+1] != var:
                        break
                else:       # If inner loop isn't broken
                    newTable.append(data)
                continue    # If inner loop is broken                        
            return newTable

        # Retrieve from DB by var in varDict
        varDict = procedure[1].var
        t = varDict['TRAIN']
        dc = varDict['DCITY']
        ac = varDict['ACITY']
        dt = varDict['DTIME']
        at = varDict['ATIME']
        rt = varDict['RUNTIME']

        retrievalDB = {}
        retrievalDB['TRAIN'] = retrieveTable(database['TRAIN'], [t])
        retrievalDB['DTIME'] = retrieveTable(database['DTIME'], [t, dc, dt])
        retrievalDB['ATIME'] = retrieveTable(database['ATIME'], [t, ac, at])
        retrievalDB['RUN-TIME'] = retrieveTable(database['RUN-TIME'], [t, dc, ac, rt])

        # print(retrievalDB)
        # print(varDict)

        # Get infor for query
        query = procedure[0]
        if query.name == 'PRINT-ALL':
            # Tàu hỏa nào?
            if query.var == '?t':
                if ('?' not in ac or '?' not in at) and len(retrievalDB['ATIME']) > 0:
                    result = ' '.join(data[1] for data in retrievalDB['ATIME'])
                elif ('?' not in dc or '?' not in dt) and len(retrievalDB['DTIME']) > 0:
                    result = ' '.join(data[1] for data in retrievalDB['DTIME'])
                else:
                    result = 'Không tìm thấy tàu hỏa được hỏi!'

            # Thời gia .. là mấy giờ?
            elif query.var == '?rt' and len(retrievalDB['RUN-TIME']) > 0:
                result = ' '.join(data[4] for data in retrievalDB['RUN-TIME'])

            # ... chạy lúc mấy giờ?
            elif query.var == '?dt' and len(retrievalDB['DTIME']) > 0:
                result = ' '.join(data[3] for data in retrievalDB['DTIME'])

            # ... đến lúc mấy giờ?
            elif query.var == '?at' and len(retrievalDB['ATIME']) > 0:
                result = ' '.join(data[3] for data in retrievalDB['ATIME'])

            else:
                result = 'Không tìm thấy thời gian được hỏi!'

        else:  # 'CHECK-ALL-TRUE'
            if ('?' not in ac or '?' not in at) and len(retrievalDB['ATIME']) > 0:
                result = 'Có.'
            elif ('?' not in dc or '?' not in dt) and len(retrievalDB['DTIME']) > 0:
                result = 'Có.'
            elif ('?' not in rt) and len(retrievalDB['RUN-TIME']) > 0:
                result = 'Có.'
            else:
                result = 'Không!'

        return result

    def retrieveResult(self, db_path):
        db = self.fetchDatabase(db_path)
        result = []
        for proc in self.procSemantics:
            result.append(self.retrieve(proc, db))
            
        return result
