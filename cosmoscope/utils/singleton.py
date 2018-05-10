class Singleton(type):
    """
    Simple implementation of the Singleton pattern.
    """
    def __init__(cls, name, bases, members):
        super(Singleton, cls).__init__(name, bases, members)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kwargs)

        return cls.instance
