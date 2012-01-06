#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import copy
from traceback import print_exc

from BaseThread import BaseThread

class HookThread(BaseThread):
    """thread for hooks"""

    def __init__(self, m, function, args, kwargs):
        """Constructor"""
        BaseThread.__init__(self, m)

        self.f = function
        self.args = args
        self.kwargs = kwargs

        self.active = []

        m.localThreads.append(self)

        self.start()

    def getActiveFiles(self):
        return self.active

    def addActive(self, pyfile):
        """ Adds a pyfile to active list and thus will be displayed on overview"""
        if pyfile not in self.active:
            self.active.append(pyfile)

    def finishFile(self, pyfile):
        if pyfile in self.active:
            self.active.remove(pyfile)

        pyfile.finishIfDone()

    def run(self):
        try:
            try:
                self.kwargs["thread"] = self
                self.f(*self.args, **self.kwargs)
            except TypeError, e:
                #dirty method to filter out exceptions
                if "unexpected keyword argument 'thread'" not in e.args[0]:
                    raise

                del self.kwargs["thread"]
                self.f(*self.args, **self.kwargs)
        except Exception, e:
            if hasattr(self.f, "im_self"):
                hook = self.f.im_self
                hook.logError(_("An Error occured"), e)
                if self.m.core.debug:
                    print_exc()
                    self.writeDebugReport(hook.__name__, plugin=hook)

        finally:
            local = copy(self.active)
            for x in local:
                self.finishFile(x)

            self.m.localThreads.remove(self)