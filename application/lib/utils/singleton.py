class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        elif args or kwargs:
            raise ValueError(
                "Cannot specify new init params for {}".format(cls.__name__)
            )

        return cls._instances[cls]


class Constant:
    frozen = False

    def __init__(self, *args, **kwargs):
        self.initialize(*args, **kwargs)
        self.frozen = True

    def __setattr__(self, *args, **kwargs):
        if self.frozen:
            raise ValueError("Cannot modify {}".format(self.__class__.__name__))
        else:
            super().__setattr__(*args, **kwargs)

    def initialize(self, *args, **kwargs):
        raise NotImplementedError


class ConstantSingleton(Constant, metaclass=Singleton):
    pass
