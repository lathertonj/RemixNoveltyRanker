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

f = open('bpms.txt', 'a')


for release in releases:
    path = os.path.realpath('../anjuna_symlinks/' + release)
    release_name = '/'.join(path.split('/')[-2:])
    
    bpm = raw_input(release_name + "? ")
    if bpm == "":
        print "passing"
        print ""
        continue
    try:
        int(bpm)
    except:
        print "bpm was not int.  continuing"
        continue
    f.write(release + "," + bpm + "\n")
    print ""