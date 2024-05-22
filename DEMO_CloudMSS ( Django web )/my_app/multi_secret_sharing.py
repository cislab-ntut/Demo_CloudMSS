import random 
import numpy as np
from math import ceil 
from decimal import *


global field_size           # field_size = size of coeff's randomness
field_size = 100

# Mersenne Prime 4th(7) 5th(13) 6th(17) 7th(19) 8th(31) = 127, 8191, 131071, 524287, 2147483647
PRIME = 2**19 - 1

# ====

def polynom(x, coeff):      # Evaluates a polynomial in x with coefficient list

    coeff_num = list( range(0 , len(coeff)) )
    # print(coeff_num)

    poly = []
    for i in coeff_num:
        poly.append(coeff[i] * (x**i))
    # print(poly)

    return sum(poly)

def _extended_gcd(a, b):
    """
    Division in integers modulus p means finding the inverse of the denominator modulo p. 
    < Note: inverse of A is B such that (A * B) % p == 1 >
    this can be computed via extended Euclidean algorithm (擴展歐幾里得算法，又叫「輾轉相除法」): 
    http://en.wikipedia.org/wiki/Modular_multiplicative_inverse#Computation
    """
    x = 0
    last_x = 1
    y = 1
    last_y = 0

    while b != 0:
        quot = a // b
        a, b = b, a % b

        x, last_x = last_x - quot * x, x
        y, last_y = last_y - quot * y, y
        
    return last_x, last_y

def _divmod(num, den, p):
    # Compute num / den modulo prime p
    invert, _ = _extended_gcd(den, p)
    return num * invert

# ====

def generate_Participant_Share(n):

    # Randomly generate a coefficient array for a polynomial with degree n.
    coeff = [ random.randrange(0, field_size) for _ in range(n) ]
    
    # 取得 多項式對應x座標的解，成為 n位 參與者的 share。
    shares = []
    for i in range(0, n):
        shares.append([ i+1 , round(polynom(i+1, coeff), 1) % PRIME ])
    
    return shares

def generate_Public_Shares(Participant_Share, secret, threshold):

    public_shares = []

    n = len(Participant_Share)

    for i in range(len(secret)):
    
        secret_public_share = []        # 根據公式，為 每個 secret 生成一個 n次 多項式 (可用 n + 1 個 share 恢復)。
    
        for x in range( n + 1 , 2 * n + 1 - threshold[i] + 1 ):
            
            pi_1 = 1
            for j in range( 1 , n + 1 ):
                pi_1 = pi_1 * ( ( 1 - _divmod( x , j , PRIME ) ) % PRIME )

            sum_1 = 0
            for j in range( 1 , n + 1 ):
                pi_2 = 1
                for l in range( 0 , n + 1 ):
                    if l != j:
                        pi_2 = pi_2 * ( _divmod( ( ( x - l ) % PRIME ) , ( ( j - l ) % PRIME ) , PRIME ) )
                
                sum_1 = sum_1 + (Participant_Share[j-1][1] * pi_2)
            
            result = (secret[i] * pi_1) % PRIME + (sum_1 % PRIME)

            secret_public_share.append([ x , result % PRIME ])
    
        public_shares.append(secret_public_share)

    return public_shares

# ====

def reconstructSecret(shares): 

    ''' 
    share_x = []
    for i in range(len(shares)): 
        share_x.append(shares[i][0])

    assert len(shares) == len(set(share_x)), "Points must be distinct !"

    if len(shares) < t:
        raise Exception("Need more participants")
    '''

    t = len(shares)

    # Combines shares using Lagranges interpolation 拉格朗日插值.  
    sums = 0
    
    for j in range(t) :
        yj = shares[j][1]

        prod = 1
        xj = shares[j][0] 
        for m in range(t): 
            xm = shares[m][0] 
            if m != j : 
                # 拉格朗日插值多項式，即為用share所構造出得方程式，將 x 代入 0 相當於於求出常數項，也就是直接得出secret值的結果。
                prod = prod * _divmod( xm , ( xm - xj ) , PRIME )

        prod = prod * yj
        sums = sums + prod

    # reconstruct = sums
    reconstruct = round( sums , 1 ) % PRIME

    return reconstruct

# ====

# Driver code  
if __name__ == '__main__': 
    
    print("\n====\n")
    
    # epoch = 1000
    epoch = 1

    error_occur = 0

    for e in range(epoch):

        n = 30       # 參與者數量

        Participant_Share = generate_Participant_Share(n)
        print("Participant:" , n)
        print("Participant_Share:" , Participant_Share)

        print()

        # K：multi-secret list，t：threshold list for each secret (t <= n)。
        # K = [4000, 70000, PRIME-1, 130, 20, 1, 0]
        # t = [0, 28, 11 , 17, 21, 22, 30]
        K = [20, 1, 0]
        t = [21, 22, 30]

        # public share list for each secret
        Public_Shares = generate_Public_Shares(Participant_Share, K, t)
        for i in range(len(K)):
            print("Secret:" , K[i] , "Participant_threshold:" , t[i] , "Public_Shares count:" , len(Public_Shares[i]))
            # print("Public_Shares:" , Public_Shares[i])

            pool = random.sample(Participant_Share, t[i]) 
            collect_shares = pool + Public_Shares[i]
            print('Collect_shares:', collect_shares) 

            reconstruct = reconstructSecret(collect_shares)
            print("Reconstructed secret:", reconstruct) 

            if reconstruct != K[i] :
                error_occur += 1

            print()

    if error_occur == 0:
        print("No error！")
    else:
        print("There is" , error_occur , "errors！！！")
    
    print("\n====\n")

    