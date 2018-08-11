import configparser


class Config:

    def __init__(self):
        try:
            self.config = self.read_config()
            self.engine_args = self.read_engine_arg()
            self.token = self.config['Discord']['Token']
            self.world_name = self.config['Minecraft']['World_Name']
            self.status = self.config['Discord']['Status']
            self.prefix = self.config['Discord']['Prefix']
            self.dynmap_url = self.config['Minecraft']['dynmap_url']
            self.bot_mod = self.config['Discord']['bot_mod']
        except:
            print("Invalid config file")
            quit(1)

    def read_config(self):
        config = configparser.ConfigParser()
        config.read('GeoffreyConfig.ini')

        if len(config.sections()) == 0:
            self.create_config(config)
            print("GeoffreyConfig.ini generated.")
            quit(0)

        return config

    def create_config(self, config):
        config['Discord'] = {'Token': '', 'Status': '', 'Prefix': '', }
        config['SQL'] = {'Dialect+Driver': '', 'username': '', 'password': '', 'host': '', 'port': '',
                              'database': '', 'bot_mod': ''}
        config['Minecraft'] = {'World_Name': '', 'dynmap_url': ''}
        with open('GeoffreyConfig.ini', 'w') as configfile:
            config.write(configfile)

    def read_engine_arg(self):
        driver = self.config['SQL']['Dialect+Driver']
        username = self.config['SQL']['username']
        password = self.config['SQL']['password']
        host = self.config['SQL']['host']
        port = self.config['SQL']['port']
        database_name = self.config['SQL']['database']

        engine_args = '{}://{}:{}@{}:{}/{}?charset=utf8mb4&use_unicode=1'

        return engine_args.format(driver, username, password, host, port, database_name)


bot_config = Config()
