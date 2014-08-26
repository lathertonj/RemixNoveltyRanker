import os.path

def releases():
    f = open('releases.txt')
    releases = []
    line = f.readline()
    while line != "" and line != "\n":
        releases += [line.strip()]
        line = f.readline()
    f.close()
    return releases
releases = releases()

f = open('keys.txt', 'a')

def keys():
    f = open('keys.txt')
    keys = {}
    # Number of steps above C
    line = f.readline()
    while line != "" and line != "\n":
        k, v = line.strip().split(',')
        keys[k] = v
        line = f.readline()
    f.close()
    return keys

keys = keys()

for release in releases:
    path = os.path.realpath('../anjuna_symlinks/' + release)
    release_name = '/'.join(path.split('/')[-2:])
    
    original_key = keys[str(int(float(release)))]
    
    key = raw_input(release_name + "\nSuggestion: " + original_key + ". Key? ")
    if key == "":
        print "passing"
        print ""
        continue
    f.write(release + "," + key + "\n")
    print ""