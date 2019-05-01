'''  
    Food Flakes for the Stock Fish
    
    A simple server that wraps the Universal Chess Interface of the stockfish
    chess engine.
'''
import grok
import os
import select

from subprocess import Popen, PIPE
from foodflakes import resource

class Foodflakes(grok.Application, grok.Container):
    pass

class Index(grok.View):
    def update(self):
        resource.style.need()

class API(grok.JSON):
    
    def nextMove(self, moves=None, level=2):
        
        def poll_io(proc, flags="r"):
            rlist = [proc.stdout.fileno()] if "r" in flags else []
            wlist = [proc.stdin.fileno()] if "w" in flags else []
            (rlist, wlist, xlist) = select.select(rlist, wlist, [], 5)
            rlist.extend(wlist)
            return rlist > 0
        
        def wait(proc, send, expect):
            if not poll_io(proc, "w"): return
            if len(send): proc.stdin.write("{}\n".format(send))
            proc.stdin.flush()
            if not poll_io(proc, "r"): return
            line = proc.stdout.readline()
            while line.find(expect) < 0:
                if not poll_io(proc, "r"): return
                line = proc.stdout.readline()
            return line.strip()

        binary = os.path.join(os.path.dirname(__file__), "bin/stockfish")
        proc = Popen([binary], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        
        wait(proc, "uci", "uciok")
        proc.stdin.write("setoption name Hash value 32\n")
        wait(proc, "isready", "readyok")
        if moves is None: moves = ""
        proc.stdin.write("ucinewgame\n")
        proc.stdin.write("position startpos moves {}\n".format(moves))
        bestmove = wait(proc, "go depth {}".format(level), "bestmove")
        bestmove = bestmove.split(" ")
        proc.terminate()
        if len(bestmove) > 1: return bestmove[1]

