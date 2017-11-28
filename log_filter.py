import re
try:
    with open('codingame.log', 'r') as f:
        lines = f.readlines()
        f.close()
    if not '--- DEBUG ---------------' in lines[0]:
        f = open('codingame.log', 'w')
        HEADER = r'DEBUG:'
        f.write('--- DEBUG ---------------\n')
        for line in lines:
            if re.match(HEADER, line):
                f.write(line.replace(HEADER, ''))
        f.close()
except:
    with open('codingame.log', 'w') as f:
        f.close()
