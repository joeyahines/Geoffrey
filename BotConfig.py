import configparser

def read_config():
    config = configparser.ConfigParser()
    config.read('GeoffreyConfig.ini')

    if len(config.sections()) == 0:
        create_config(config)
        print("GeoffreyConfig.ini generated.")
        quit(0)

    return config


def create_config(config):
    config['Discord'] = {'Token': ''}
    config['SQL'] = {'Dialect+Driver': '', 'username': '', 'password':'', 'host': '', 'port': '', 'database':'',
                     'test_args':''}

    with open('GeoffreyConfig.ini', 'w') as configfile:
        config.write(configfile)


def get_engine_arg(config):
    driver = config['SQL']['Dialect+Driver']
    username = config['SQL']['username']
    password = config['SQL']['password']
    host = config['SQL']['host']
    port = config['SQL']['port']
    database_name = config['SQL']['database']

    engine_args = '{}://{}:{}@{}:{}/{}'

    return engine_args.format(driver, username, password, host, port, database_name)