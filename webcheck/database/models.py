class Account:
    def __init__(
        self,
        property_id=None,
        name=None,
        path=None,
        property_deleted=None,
        property_deleted_on=None,
        contents_parked=None,
        contents_parked_on=None,
    ):
        self.property_id = property_id
        self.name = name
        self.path = path
        self.property_deleted = property_deleted
        self.property_deleted_on = property_deleted_on
        self.contents_parked = contents_parked
        self.contents_parked_on = contents_parked_on

    def __eq__(self, other):
        if other is None:
            return False
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "Account{}".format(self.__dict__)
