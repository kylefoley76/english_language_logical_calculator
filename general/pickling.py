import pickle, os

from abbreviations import *


def save_meta_pickle(obj, name):
    name += ".pkl"
    temp = open(mdir + '/meta_pickles/' + name, 'wb')
    pickle.dump(obj, temp)
    temp.close()


def save_json_proof(name, obj, mode):
    name = fdir + "json/" + name
    save_json(name, obj)


def open_json_proof(name, mode):
    name = fdir + "json/" + name
    return open_json(name, mode)


def save_json(name, obj):
    name += ".json"
    with open(name, "w") as fp:
        json.dump(obj, fp)


def open_json(name, mode='w'):
    name += ".json"
    with open(name) as fp:
        return json.load(fp)


def open_pkl_ign_error(name):
    name += ".pkl"

    pkl_file = open(fdir + 'meta_pickles/' + name, 'rb')
    obj = pickle.load(pkl_file)
    pkl_file.close()

    return obj


def save_pickle(obj, name, any_name=True):
    if not any_name:
        name = mdir + 'pickles/' + name
    elif any_name == 'hi':
        name = mdir + 'hi_pickles/' + name
    elif any_name == 'hit':
        name = mdir + 'pickles/hieroglyphs/tests/' + name

    if not name.endswith(".pkl"):
        name += ".pkl"
    temp = open(name, "wb")
    pickle.dump(obj, temp)
    temp.close()


def open_meta_pickle(name, encoding=''):
    if not name.endswith(".pkl"):
        name += ".pkl"
    try:
        os.path.exists(mdir + 'meta_pickles/' + name)
    except:
        p(f"file {mdir + 'meta_pickles/' + name} does not exist")
        raise Exception

    try:
        pkl_file = open(mdir + 'meta_pickles/' + name, 'rb')
        if encoding != "":
            obj = pickle.load(pkl_file, encoding=encoding)
        else:
            obj = pickle.load(pkl_file)
        pkl_file.close()
    except:
        p(f"could not open {name}")
        raise Exception

    return obj


def open_bpickle(name):
    name = fdir + f"byu_docs/byu_files/{name}"
    return open_pickle(name, 1)

def open_ppickle(name):
    name = fdir + f"poet_pickles/{name}"
    return open_pickle(name, 1)

def save_ppickle(obj, name):
    name = fdir + f"poet_pickles/{name}"
    return save_pickle(obj, name, 1)

def save_bpickle(obj, name):
    name = fdir + f"byu_docs/byu_files/{name}"
    return save_pickle(obj, name, 1)


def open_pickle(name, any_folder=True, warn=True):
    if "DS_Store" in name: return []

    if not name.endswith(".pkl"):
        name += ".pkl"
    if not any_folder:
        name = mdir + 'pickles/' + name
    elif any_folder == 'hi':
        name = mdir + 'hieroglyphs/hi_pickles/' + name
    files_used.add(name)
    pkl_file = open(name, 'rb')
    obj = pickle.load(pkl_file)
    pkl_file.close()

    return obj


def turn_off():
    print('turned off')
    save_pickle(0, 'bool1')


def turn_off1():
    print('turned off')
    save_pickle(0, 'bool2')


def turn_on():
    print('turned on')
    save_pickle(1, 'bool1')


def turn_on1():
    print('turned on')
    save_pickle(1, 'bool2')
