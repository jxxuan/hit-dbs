class SyntaxTree:
    def __init__(self):
        self._lfchild = None
        self._rchild = None
        self._op = ''
        self._cond = ''
        self._rel = ''

    @property
    def lfchild(self):
        return self._lfchild

    @lfchild.setter
    def lfchild(self, value):
        self._lfchild = value

    @property
    def rchild(self):
        return self._rchild

    @rchild.setter
    def rchild(self, value):
        self._rchild = value

    @property
    def op(self):
        return self._op

    @op.setter
    def op(self, value):
        self._op = value

    @property
    def cond(self):
        return self._cond

    @cond.setter
    def cond(self, value):
        self._cond = value

    @property
    def rel(self):
        return self._rel

    @rel.setter
    def rel(self, value):
        self._rel = value
