import csv
with open('test.csv', mode='r', newline='') as file:
    csvFile = csv.reader(file)
    headers = next(csvFile)  # Get the header row
    print("Headers:", headers)
    for row in csvFile:
        print(row)

