__author__ = 'thor'

import util.log as util_log
import util.pobj as util_pobj
import pdict.get as pdict_get
import util.ulist as util_ulist
import pandas as pd


class DataFlow(object):
    """
    DataFlow is a framework to pipeline data processes.
    """
    def __init__(self, obj):
        [setattr(self, k, v) for k, v in obj.__dict__.iteritems()]
        if not hasattr(self, 'data_dependencies'):
            self.data_dependencies = dict()
        if not hasattr(self, 'data_makers'):
            self.data_makers = dict()
        if not hasattr(self, 'data_storers'):
            self.data_storers = dict()
        # make sure values of data_dependencies are lists
        self.data_dependencies = {k: util_ulist.ascertain_list(v) for k, v in self.data_dependencies.iteritems()}
        ## mark all data_maker_types that already exist as "call"
        #self.data_maker_type = {k: 'call' for k in self.data_makers.keys()}
        # default data_makers to functions of the same name as data_dependencies
        missing_data_makers = set(self.data_dependencies.keys()).difference(self.data_makers.keys())
        for k in self.data_dependencies.keys():
            #if k in self.data_makers.keys():  # if the data_maker was already given
            #
            if hasattr(self, k):
                k_attr = getattr(self, k)
                if isinstance(k_attr, pd.HDFStore):  # if k_attr is a store
                    self.data_makers[k] = StoreDataGetter(store=k_attr, key=k)
                elif hasattr(k_attr, '__call__'):  # if k_attr is callable (method, function, ...)
                    self.data_makers[k] = CallDataGetter(fun=k_attr)
                else:  # if not, assume there is, or will be, an attribute of that name, and have data_maker return it
                    self.data_makers[k] = AttrDataGetter(obj=self, attr=k_attr)
        if not hasattr(self, 'verbose_level'):
            self.verbose_level = 1

    def put_in_store(self, name, data):
        util_log.printProgress('  Storing %s in store' % name)
        self.store.put(name, data)

    def put_in_attr(self, name, data):
        util_log.printProgress('  Storing %s in attribute' % name)
        setattr(self, name, data)

    def get_data(self, data_name, **kwargs):
        #if data_name not in self.data_dependencies.keys():
        #    raise ValueError("I have no data_dependencies for %s" % data_name)
        if hasattr(self, 'store') and self.store.has_key(data_name):  # if no data is input and the data exists in the store...
                # return the stored data
                self.print_progress(2, '  Getting %s from store' % data_name)
                return self.store[data_name]
        elif util_pobj.has_non_callable_attr(self, data_name):
            return getattr(self, data_name)
        else:
            # determine what the data part of kwargs is
            input_data, kwargs = pdict_get.get_subdict_and_remainder(kwargs, self.data_dependencies[data_name])
            # determine what data we don't have
            missing_data_names = set(self.data_dependencies[data_name]).difference(input_data.keys())
            # get the data we don't have
            if missing_data_names:
                self.print_progress(3, "  --> %s requires %s" % (data_name, ', '.join(missing_data_names)))
                for missing_dependency in missing_data_names:
                    input_data[missing_dependency] = \
                        self.get_data(data_name=missing_dependency, **kwargs)
        # make the data
        if data_name in self.data_makers.keys():
            # here the data needs to be made from data
            self.print_progress(1, '  Making %s' % data_name)
            kwargs = dict(input_data, **kwargs)
            made_data = self.data_makers[data_name](**kwargs)
            # store it if necessary
            if data_name in self.data_storers.keys() and self.data_storers[data_name] is not None:
                self.data_storers[data_name](data_name, made_data)
            return made_data
        else:
            # here all you want is the input_data
            return input_data

    def print_progress(self, min_level, msg='', verbose_level=None):
        verbose_level = verbose_level or self.verbose_level
        if verbose_level >= min_level:
            msg = 2 * min_level * ' ' + msg
            util_log.printProgress(msg)

    @staticmethod
    def verbose(kwargs, min_level=1):
        return ('verbose' in kwargs.keys()) and (kwargs['verbose'] >= min_level)


class StoreDataGetter(object):
    def __init__(self, store, key):
        self.store = store
        self.key = key

    def get_data(self, *args, **kwargs):
        return self.store[self.key]


class AttrDataGetter(object):
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr

    def get_data(self, *args, **kwargs):
        return getattr(self.obj, self.attr)


class CallDataGetter(object):
    def __init__(self, fun):
        self.fun = fun

    def get_data(self, *args, **kwargs):
        return self.fun(*args, **kwargs)

    #def get_data(self, data_name, **kwargs):
    #    #if data_name not in self.data_dependencies.keys():
    #    #    raise ValueError("I have no data_dependencies for %s" % data_name)
    #    if hasattr(self, 'store') and self.store.has_key(data_name):  # if no data is input and the data exists in the store...
    #            # return the stored data
    #            self.print_progress(2, '  Getting %s from store' % data_name)
    #            return self.store[data_name]
    #    elif util_pobj.has_non_callable_attr(self, data_name):
    #        return getattr(self, data_name)
    #    else:
    #        # determine what the data part of kwargs is
    #        input_data, kwargs = pdict_get.get_subdict_and_remainder(kwargs, self.data_dependencies[data_name])
    #        # determine what data we don't have
    #        missing_data_names = set(self.data_dependencies[data_name]).difference(input_data.keys())
    #        # get the data we don't have
    #        if missing_data_names:
    #            self.print_progress(3, "  --> %s requires %s" % (data_name, ', '.join(missing_data_names)))
    #            for missing_dependency in missing_data_names:
    #                input_data[missing_dependency] = \
    #                    self.get_data(data_name=missing_dependency, **kwargs)
    #    # make the data
    #    if data_name in self.data_makers.keys():
    #        # here the data needs to be made from data
    #        self.print_progress(1, '  Making %s' % data_name)
    #        kwargs = dict(input_data, **kwargs)
    #        made_data = self.data_makers[data_name](**kwargs)
    #        # store it if necessary
    #        if data_name in self.data_storers.keys() and self.data_storers[data_name] is not None:
    #            self.data_storers[data_name](data_name, made_data)
    #        return made_data
    #    else:
    #        # here all you want is the input_data
    #        return input_data