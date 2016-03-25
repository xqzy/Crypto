#!/usr/bin/env python
#
# Copyright AlertAvert.com (c) 2013. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import utils


__author__ = 'marco'

import gmpy2
from gmpy2 import (add, ceil, div, isqrt,
                   mpz, mul, sqrt, sub)


class Factoring(object):
    """ Used to factor a large integer N in its prime components p,q
        Solves the Programming Assignment of Week 6:
        https://class.coursera.org/crypto-011/quiz/attempt?quiz_id=100
    """

    def __init__(self, n):
        self.n = n
        #self.log = utils.ProgressReporter()

    def _check_sol(self, p, q):
        if gmpy2.is_prime(p) and gmpy2.is_prime(q):
            return sub(self.n, mul(p, q)) < 0.5
        return False

    def calc_near(self):
        a = ceil(sqrt(self.n))
        p, q = self._calc_factors(a)
        assert self._check_sol(p, q)
        assert gmpy2.is_prime(p)
        return p, q

    def calc_brute_force(self):
        a = ceil(sqrt(self.n))
        for n in xrange(1, 2 ** 20):
            p, q = self._calc_factors(add(a, n))
            if self._check_sol(p, q):
                return p, q
            #self.log.print_progress(n)
        else:
            raise ValueError("Cannot factor {}".format(self.n))

    @staticmethod
    def solve_quadratic(a, b, c):
        """ Solves the quadratic equation ```a x2 + b x + c = 0```
        :return: the GMP result of solving the quadratic equation usign multi-precision numbers
        """
        bb = sqrt(sub(mul(b, b), mul(mpz(4), mul(a, c))))
        x1 = gmpy2.div(sub(-b, bb), mul(mpz(2), a))
        x2 = gmpy2.div(add(-b, bb), mul(mpz(2), a))
        return x1, x2

    def calc_near6(self):
        """ Solves the Extra Credit question Q3
        See:
        Uses only integer arithmetic to avoid issues with rounding errors
        Solution credit to Francois Degros:
        https://class.coursera.org/crypto-011/forum/thread?thread_id=517#post-2279
        :return: the prime factors of ```self.n```, p and q
        :rtype: tuple
        """
        # A = ceil(sqrt(24 N))  - the use of isqrt() won't matter, as we seek the ceil
        A = add(isqrt(mul(self.n, mpz(24))), mpz(1))
        # D = A^2 - 24 N
        D = sub(mul(A, A), mul(24, self.n))
        # E = sqrt(D)  - note D is a perfect square and we can use integer arithmetic
        E = isqrt(D)
        assert sub(mul(E, E), D) == mpz(0)
        p = div(sub(A, E), 6)
        q = div(add(A, E), 4)
        if self._check_sol(p, q):
            return p, q
        # The above is the right solution, however, there is another possible solution:
        p = div(add(A, E), 6)
        q = div(sub(A, E), 4)
        if self._check_sol(p, q):
            return p, q
        print 'Could not find a solution'
        return 0, 0

    def _calc_factors(self, a):
        x = sqrt(sub(mul(a, a), self.n))
        p = sub(a, x)
        q = add(a, x)
        return mpz(p), mpz(q)


# ############
#
# Challenges:

N1 = '17976931348623159077293051907890247336179769789423065727343008115' \
     '77326758055056206869853794492129829595855013875371640157101398586' \
     '47833778606925583497541085196591615128057575940752635007475935288' \
     '71082364994994077189561705436114947486504671101510156394068052754' \
     '0071584560878577663743040086340742855278549092581'

N2 = '6484558428080716696628242653467722787263437207069762630604390703787' \
    '9730861808111646271401527606141756919558732184025452065542490671989' \
    '2428844841839353281972988531310511738648965962582821502504990264452' \
    '1008852816733037111422964210278402893076574586452336833570778346897' \
    '15838646088239640236866252211790085787877'

N3 = '72006226374735042527956443552558373833808445147399984182665305798191' \
     '63556901883377904234086641876639384851752649940178970835240791356868' \
     '77441155132015188279331812309091996246361896836573643119174094961348' \
     '52463970788523879939683923036467667022162701835329944324119217381272' \
     '9276147530748597302192751375739387929'

CIPHER = '2209645186741038177630656113488341801741006978789283107173183914' \
         '3676135600120538004282329650473509424343946219751512256465839967' \
         '9428894607645420405815647489880137348641204523252293201764879166' \
         '6640299750918872997169052608322206777160001932926087000957999372' \
         '4077458967773697817571267229951148662959627934791540'


def solve_q1():
    factor = Factoring(mpz(N1))
    print_pq(*factor.calc_near())


def solve_q2():
    factor = Factoring(mpz(N2))
    print_pq(*factor.calc_brute_force())


def solve_q3():
    factor = Factoring(mpz(N3))
    print_pq(*factor.calc_near6())


def decrypt():
    n = mpz(N1)
    p, q = Factoring(n).calc_near()
    fi_n = mul(sub(p, 1), sub(q, 1))
    e = mpz(65537)
    d = gmpy2.invert(e, fi_n)
    dec = gmpy2.powmod(mpz(CIPHER), d, n)
    
    dec_hex = hex(dec)
    if dec_hex.startswith('0x2'):
        msg_starts = dec_hex.index('00') + 2
        msg_hex = dec_hex[msg_starts:]
        return msg_hex.decode('hex')
    print 'Decryption failed'


def print_pq(p, q):
    print "The result is:\np = {},\nq = {}\n".format(p, q)


def main():
    # Configure precision to deal with large integers
    # The right factor(3) must be found by trial and error; turns out that to solve these
    # problems a precision of around 900 digits is necessary
    num_digits = len(N1)
    precision = 3 * num_digits
    print "The required precision is {} digits".format(precision)
    gmpy2.get_context().precision = precision
    print "Q1)"
    solve_q1()
    print "Q2)"
    solve_q2()
    print "Q3)"
    solve_q3()
    print "Decrpyt:", decrypt()

if __name__ == "__main__":
    main()