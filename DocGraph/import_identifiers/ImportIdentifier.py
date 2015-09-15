
from abc import ABCMeta, abstractmethod


class ImportIdentifier:
    __metaclass__ = ABCMeta

    @abstractmethod
    def can_help(self, filepath):
        '''
            returns True if this class can identify imports in this file, False o/wise
        '''
        pass

    @abstractmethod
    def get_imports(self, text):
        '''
            return a set() of files that the text imports
        '''
        pass
