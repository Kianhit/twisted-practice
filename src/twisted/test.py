import traceback, sys
from twisted.python import log
from twisted.internet import defer

def hello():
    print 'hello man'
    print 'Lately I feel like I\'m stuck in rut.Go fighting, fearlessly!!'
    traceback.print_stack()

class Countdown(object):
    counter = 5
    
    def count(self):
        if self.counter == 0:
            reactor.stop()
        else:
            print '%d %s' % (self.counter , '...')
            self.counter -= 1
            reactor.callLater(1, self.count) # 1 here is the number of seconds in the future you would like your callback to run. 

def falldown():
    raise Exception('I fall down')

def upagain():
    raise Exception('But I get up again')

def bad_callback(arg1):
    xxx

def on_error(failure):
    log.err('The next function call will log the failure as an error.')
    log.err(failure)

def testlog():
    log.msg('This will not be logged, we have not installed a logger.')
    log.startLogging(sys.stdout)
    log.msg('Log msg 1')
    log.err('Log err 1')
    try:
        bad_callback()
    except:
        log.err('The next function call will log the traceback as an error.')
        log.err()
    
    d = defer.Deferred()
    d.addCallback(bad_callback)
    d.addErrback(on_error)
    d.callback(True)

from twisted.internet import reactor

# reactor.callWhenRunning(hello)
# reactor.callWhenRunning(Countdown().count)
# reactor.callWhenRunning(falldown)
# reactor.callWhenRunning(upagain)
reactor.callWhenRunning(testlog)
print 'Starting the reactor'
reactor.run()
print 'The reactor stops'