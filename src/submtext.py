import sys
import struct

def submission_text(filename):
    f = open(filename, 'rb')
    magic, team, scenario = struct.unpack('<III', f.read(12))
    print 'Team:     %5d' % team
    print 'Scenario: %5d' % scenario
    print
    frame = 0
    time, count = struct.unpack('<II', f.read(8))
    while count > 0:
        print 'Frame: %d, t=%d' % (frame, time)
        for port in range(count):
            address, value = struct.unpack('<Id', f.read(12))
            print 'Port %d: %f' % (address, value)
        print
        time, count = struct.unpack('<II', f.read(8))
        frame += 1
    f.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        submission_text(sys.argv[1])