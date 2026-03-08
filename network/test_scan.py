from network import advancedscanner as a

print('small scan:')
a.portScan('localhost', [22,80])

print('\n--- large scan ---')
a.portScan('localhost', list(range(1,10001)))
