import copy


# Fibonnaci generation is handled by this class
class FibNumbers:
    def __init__(self):
        # In this case, the first fib number is 1. There is no zeroth fib number
        self.__fibNumbers = [1, 1]

    def getNthFibNumber(self, n):
        if n == 0:
            raise ValueError("For our cases, there is no zeroth fib number")
        elif n < 0:
            raise ValueError("Can't have a negative fib number.")
        elif n <= len(self.__fibNumbers):
            return self.__fibNumbers[n - 1]
        else:
            # Need to calculate the number using dynamic programming
            for i in range(len(self.__fibNumbers), n):
                self.__fibNumbers.append(
                    self.__fibNumbers[i - 1] + self.__fibNumbers[i - 2]
                )

            return self.__fibNumbers[n - 1]

    @property
    def fibNumbers(self):
        # To make it impossible for other code to tamper with the values
        return copy.deepcopy(self.__fibNumbers)

    # Returns a generator that contains all fib numbers
    # correlating to the numbers in the number sequence
    def fibGenerator(self, numSeq):
        for i in numSeq:
            yield self.getNthFibNumber(i)

    def isXAFibNumber(self, x):
        i = 1
        while True:
            if self.getNthFibNumber(i) == x:
                return True
            elif self.getNthFibNumber(i) > x:
                return False
            i += 1


fibNumbers: FibNumbers = FibNumbers()
