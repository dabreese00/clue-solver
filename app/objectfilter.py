# TODO: Make this class immutable?
class ObjectFilter:
    """Represents a filter to match custom objects of any kind.

    The filter is represented as a binary tree structure; this allows building
    compound filters by joining independent filters using a logical operator.

    Public methods:
        match      -- check a single object against the filter
        add        -- add a filter condition to the query
        get        -- query a list and return results based on the filter

    Instance variables:
        left       -- left child filter
        right      -- right child filter
        statement  -- this node's filter component
    """
    def __init__(self, statement=None):
        """Initialize a leaf filter.

        The filter's specific matching behavior is based on `statement`, and is
        defined in the self.match method.

        Arguments:
            statement -- defines what objects this filter should match
        """
        self.left = None
        self.right = None
        self.statement = statement

    def match(self, obj):
        """Recursively check if obj matches all filter statements.

        Arguments:
            obj -- the object to check
        """
        if self.statement == "and":
            return self.left.match(obj) and self.right.match(obj)
        elif self.statement == "or":
            return self.left.match(obj) or self.right.match(obj)
        elif self.statement == "not":
            return not self.left.match(obj)
        else:
            return NotImplemented

    def compound(self, op="not", other_filter=None):
        """Create a compound filter using a logical operator.

        Arguments:
            op           -- logical operator to use
            other_filter -- other filter to combine with, if op is "and"/"or"
        """
        if op in ["and", "or", "not"]:
            new = ObjectFilter(op)
            new.left = self
            new.right = other_filter
            return new
        else:
            raise ValueError("Specified op was {}; ".format(op) +
                             "expected 'and', 'or', or 'not'")

    def __add__(self, other):
        """Combine with another filter to create a compound "and" filter."""
        return self.compound(op="and", other_filter=other)

    def __truediv__(self, other):
        """Combine with another filter to create a compound "or" filter."""
        return self.compound(op="or", other_filter=other)

    def __neg__(self):
        """Invert filter, creating a compound "not" filter."""
        return self.compound(op="not")

    def get(self, objlist):
        """Return all items from objlist that match the filter."""
        matching = []
        for obj in objlist:
            if self.match(obj):
                matching.append(obj)
        return matching
