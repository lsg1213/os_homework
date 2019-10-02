#! /usr/bin/env python

import sys
from optparse import OptionParser
import random

parser = OptionParser()
parser.add_option("-s", "--seed", default=0, help="the random seed", 
                  action="store", type="int", dest="seed")
parser.add_option("-j", "--jobs", default=3, help="number of jobs in the system",
                  action="store", type="int", dest="jobs")
parser.add_option("-l", "--jlist", default="", help="instead of random jobs, provide a comma-separated list of run times",
                  action="store", type="string", dest="jlist")
parser.add_option("-m", "--maxlen", default=10, help="max length of job",
                  action="store", type="int", dest="maxlen")
parser.add_option("-p", "--policy", default="FIFO", help="sched policy to use: SJF, FIFO, RR, STCF",
                  action="store", type="string", dest="policy")
parser.add_option("-q", "--quantum", help="length of time slice for RR policy", default=1, 
                  action="store", type="int", dest="quantum")
parser.add_option("-c", help="compute answers for me", action="store_true", default=False, dest="solve")

(options, args) = parser.parse_args()

random.seed(options.seed)


print ('ARG policy ' + options.policy)
if options.jlist == '':
    print 'ARG jobs', options.jobs
    print 'ARG maxlen', options.maxlen
    print 'ARG seed', options.seed
else:
    print 'ARG jlist', options.jlist

print ''

print 'Here is the job list, with the run time of each job: '

import operator
joblist = []
if options.jlist == '':
    for jobnum in range(0,options.jobs):
        runtime = int(options.maxlen * random.random()) + 1
        arrivaltime = 0
        arrivaltime = int(options.maxlen * random.random()) + 1
        joblist.append([jobnum, arrivaltime, runtime])
        print '  Job', jobnum, '( arrival time = ' + str(arrivaltime) + '  length = ' + str(runtime) + ' )'
else:
    jobnum = 0
    print('Please set the arrival time of the list')
    for runtime in options.jlist.split(','):
        joblist.append([jobnum, float(input('length = %.2lf \'s arrival time: ' % float(runtime))), float(runtime)])
        jobnum += 1
    for job in joblist:
        print '  Job', job[0], '( arrival time = ' + str(job[1]) + '  length = ' + str(job[2]) + ' )'
print '\n'

if options.solve == True:
    print '** Solutions **\n'
    if options.policy == 'SJF':
        l = {}
        for i in joblist:
            l[i[1]] = []
        for i in joblist:
            l[i[1]].append(i)
        joblist = []
        for i in l:
            l[i] = sorted(l[i], key=lambda a: a[2])
            for j in l[i]:
                joblist.append(j)
        
        tmplist = []
        thetime = 0
        print 'Execution trace:'
        for job in joblist:
            if thetime < job[1]: 
                thetime = job[1]
            print '  [ time %3d ] Run job %d which is arrived at %.2f for %.2f secs ( DONE at %.2f )' % (thetime, job[0], job[1], job[2], thetime + job[2])
            tmplist.append([job[0],thetime-job[1],thetime + job[2] - job[1]])   # jobnum, response time, turnaround time
            thetime += job[2]

        print '\nFinal statistics:'
        t     = joblist[0][1]
        count = 0
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0

        tmplist = sorted(tmplist, key=lambda a: a[0])
        for tmp in tmplist:

            response = tmp[1]
            turnaround = tmp[2]
            wait       = tmp[1]
            print '  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (tmp[0], response, turnaround, wait)
            responseSum   += response
            turnaroundSum += turnaround
            waitSum       += wait
            count = count + 1
        print '\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count)
    
    if options.policy == 'FIFO':    #success to modify
        thetime = 0
        print 'Execution trace:'
        joblist = sorted(joblist, key=lambda a: a[1])
        turn = {}
        wait = {}
        res = {}
        for job in joblist:
            if thetime < job[1]: 
                thetime = job[1]
            print '  [ time %3d ] Run job %d which is arrived at %.2f for %.2f secs ( DONE at %.2f )' % (thetime, job[0], job[1], job[2], thetime + job[2])
            res[job[0]] = thetime - job[1]
            turn[job[0]] = thetime + job[2] - job[1]
            wait[job[0]] = thetime - job[1]
            thetime += job[2]

        print '\nFinal statistics:'
        t     = 0.0
        count = 0
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        joblist = sorted(joblist, key=lambda a: a[0])
        for job in joblist:
            
            print '  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (job[0], res[job[0]], turn[job[0]], wait[job[0]])
            responseSum   += res[job[0]]
            turnaroundSum += turn[job[0]]
            waitSum       += wait[job[0]]
        count = len(joblist)
        print '\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count)
                     
    if options.policy == 'RR':
        print 'Execution trace:'
        turnaround = {}
        response = {}
        lastran = {}
        wait = {}
        quantum  = float(options.quantum)
        jobcount = len(joblist)
        for i in range(0,jobcount):
            lastran[i] = 0.0
            wait[i] = 0.0
            turnaround[i] = 0.0
            response[i] = -1

        runlist = []
        for e in joblist:
            runlist.append(e)

        # sorting
        li = []
        joblist = sorted(joblist, key=lambda a:a[1])    # stable sort
        runlist = []
        timelist = {}
        turn = {}
        wait = {}
        res = {}
        for i in joblist:
            timelist[i[0]] = 0
            turn[i[0]] = -1
            wait[i[0]] = -1
            res[i[0]] = -1
        runtime = joblist[0][1] # arrival time of first job

        while len(timelist) != 0:
            for job in joblist:
                try:
                    if (res[job[0]] == -1):
                        res[job[0]] = runtime
                    timelist[job[0]] += options.quantum
                    if (int(timelist[job[0]]) >= int(job[2])):
                        timelist[job[0]] = float(job[2])
                        if (int(timelist[job[0]]) == int(job[2])):
                            print '  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (runtime, job[0], options.quantum, runtime + options.quantum)
                            turn[job[0]] = runtime + options.quantum
                            runtime += options.quantum
                        else:
                            print '  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (runtime, job[0], job[2] % options.quantum, runtime + job[2] % options.quantum)
                            turn[job[0]] = runtime + job[2] % options.quantum
                            runtime += job[2] % options.quantum
                        del timelist[job[0]]
                    else:
                        print '  [ time %3d ] Run job %3d for %.2f secs' % (runtime, job[0], options.quantum)
                        runtime += options.quantum
                except:
                    continue

        for i in joblist:
            wait[i[0]] = turn[i[0]] - i[1] - i[2]
            turn[i[0]] -= i[1]
            res[i[0]] -= i[1]


        print '\nFinal statistics:'
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for i in joblist:
            turnaroundSum += turn[i[0]]
            responseSum += res[i[0]]
            waitSum += wait[i[0]]
            print '  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i[0], res[i[0]], turn[i[0]], wait[i[0]])
        count = len(joblist)
        
        print '\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count)

    if options.policy == 'STCF':
        # sorting
        joblist = sorted(sorted(joblist, key=lambda a: a[2]), key=lambda a: a[1])
        runtime = joblist[0][1]
        rearrange = []
        turn = {}
        wait = {}
        res = {}
        runlist = []    # jobnum
        for i in joblist:
            i.append(i[2]) # joblist[i][3] remain = joblist[i][2] initializing
            rearrange.append(i[1])
            res[i[0]] = 10000000
        rearrange = sorted(list(set(rearrange)))
        keep = []
        check = False
        for re in range(len(rearrange)):
            for i in joblist:
                if i[1] == rearrange[re]:
                    runlist.append(i)
            
            runlist = sorted(runlist,key=lambda a: a[3])
            if len(keep) != 0:
                if keep[1] != runlist[0][0] and check:
                    print '  [ time %3d ] Run job %3d for %.2f secs' % (keep[0], keep[1], keep[2])
                    runlist[keep[1]][3] -= rearrange[re] - runtime
                    if (res[keep[1]] > runtime):
                        res[keep[1]] = runtime
                    runtime += rearrange[re] - runtime
                    keep = []
            if re + 1 <= len(rearrange) - 1:
                if rearrange[re + 1] > runtime + runlist[0][3]:
                    print '  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (runtime, runlist[0][0], runlist[0][3], runtime + runlist[0][3])
                    turn[runlist[0][0]] = runtime + runlist[0][3] - runlist[0][1]
                    wait[runlist[0][0]] = runtime + runlist[0][3]
                    if (res[runlist[0][0]] > runtime):
                        res[runlist[0][0]] = runtime
                    runtime += runlist[0][3]
                    del runlist[0]
                    keep = []
                    re -= 1
                    continue
                elif rearrange[re + 1] == runtime + runlist[0][3]:
                    print '  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (runtime, runlist[0][0], runlist[0][3], runtime + runlist[0][3])
                    turn[runlist[0][0]] = runtime + runlist[0][3] - runlist[0][1]
                    wait[runlist[0][0]] = runtime + runlist[0][3]
                    if (res[runlist[0][0]] > runtime):
                        res[runlist[0][0]] = runtime
                    runtime += runlist[0][3]
                    del runlist[0]
                    keep = []
                    continue
                else:
                    keep = [runtime, runlist[0][0], rearrange[re + 1] - runtime]
                    check = True
                    continue

            else:
                while len(runlist) != 0:
                    print '  [ time %3d ] Run job %3d for %.2f secs ( DONE at %.2f )' % (runtime, runlist[0][0], runlist[0][3], runtime + runlist[0][3])
                    turn[runlist[0][0]] = runtime + runlist[0][3] - runlist[0][1]
                    wait[runlist[0][0]] = runtime + runlist[0][3]
                    if (res[runlist[0][0]] > runtime):
                        res[runlist[0][0]] = runtime
                    runtime += runlist[0][3]
                    del runlist[0]
 
        
        print '\nFinal statistics:'
        turnaroundSum = 0.0
        waitSum       = 0.0
        responseSum   = 0.0
        for i in joblist:
            wait[i[0]] -= i[1] + i[2]
            res[i[0]] -= i[1]
        
        for i in joblist:
            turnaroundSum += turn[i[0]]
            responseSum += res[i[0]]
            waitSum += wait[i[0]]
            print '  Job %3d -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f' % (i[0], res[i[0]], turn[i[0]], wait[i[0]])
        count = len(joblist)
        
        print '\n  Average -- Response: %3.2f  Turnaround %3.2f  Wait %3.2f\n' % (responseSum/count, turnaroundSum/count, waitSum/count)
        


    if options.policy != 'FIFO' and options.policy != 'SJF' and options.policy != 'RR' and options.policy != 'STCF': 
        print 'Error: Policy', options.policy, 'is not available.'
        sys.exit(0)
else:
    print 'Compute the turnaround time, response time, and wait time for each job.'
    print 'When you are done, run this program again, with the same arguments,'
    print 'but with -c, which will thus provide you with the answers. You can use'
    print '-s <somenumber> or your own job list (-l 10,15,20 for example)'
    print 'to generate different problems for yourself.'
    print ''



