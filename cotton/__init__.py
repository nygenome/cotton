from fabric.api import env

# make an env-callback collection here, and importing a module adds to that collection.
# setup_env then calls everything in the collection after setting the overrides explicitly.
setup_functions = []


def set_env(key, value, **overrides):
    '''Puts the key-value pair into env unless the key is present
    in overrides.  Meant for use with setup_env.'''
    if key not in overrides:
        env[key] = value

def setup_env(**overrides):
    '''
    Sets up the environment, using the appropriate cascades.  This emulates
    lazy property definitions, so updates to e.g. env.app_root that occur after
    env.app_root has been used to define another property will be reflected in
    that subsequent property.
    '''

    for k,v in overrides.items():
        set_env(k,v)

    for func in setup_functions:
        func(**overrides)

def register_setup(func):
    setup_functions.append(func)
