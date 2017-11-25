import csv

violations = {}

with open('DOHMH_New_York_City_Restaurant_Inspection_Results.csv') as csvfile:
    next(csvfile)
    reader = csv.reader(csvfile)
    for row in reader:
        restID = int(row[0])
        vioCode = row[10]
        
        if vioCode == '':
            continue
        
        if restID not in violations:
            violations[restID] = []
        violations[restID].append(vioCode)

with open('INTEGRATED-DATASET.csv', 'w') as file:
    for key in violations.keys():
        file.write(', '.join(violations[key]))
        file.write('\n')