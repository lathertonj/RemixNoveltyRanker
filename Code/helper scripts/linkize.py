from subprocess import check_output

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

for r in releases:
    #filepath = raw_input(r + "? ")
    #if filepath == "":
    #    print "passing \n"
    #    continue
    # No python! Stop escaping things!
    # My problem is that python doesn't escape spaces and unix does T_T
    #filepath = "'" + filepath.replace('\\', '').strip() + "'"
    #print repr(filepath)
    # Link the thing to the thing
    #symlink = "../anjuna_symlinks/" + r
    nop = check_output(["./linkrelease.sh", r])
    print ""