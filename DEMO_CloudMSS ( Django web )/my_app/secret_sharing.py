import random 
import numpy as np
from math import ceil 
from decimal import *


global field_size   # field_size = size of coeff's randomness == (random_size)
field_size = 100

# Mersenne Prime 4th(7) 5th(13) 6th(17) 7th(19) 8th(31) = 127, 8191, 131071, 524287, 2147483647
PRIME = 2**19 - 1
   
def computeDelta(s1,s2):

    
    y1=(s1[0][1]-s2[0][1])
    y2=(s1[1][1]-s2[1][1])
    x=s1[0][0]-s2[1][0]

    r=(y1-y2)/x

    delta=y1-s1[0][0]*r

    if(delta<0):

        y1=(s2[0][1]-s1[0][1])
        y2=(s2[1][1]-s1[1][1])
    
        x=s1[0][0]-s2[1][0]
        
        r=(y1-y2)/x
        delta=y1-s1[0][0]*r  
        
    return(delta)

# ====

def two_party_share_Addition(P1, P2):       # 找到雙方對齊的 share 做加法。

    additive_shares = []
    for sh1 in P1:
        for sh2 in P2:
            x1, y1, x2, y2 = sh1[0], sh1[1], sh2[0], sh2[1]
            if x1 == x2:
                additive_shares.append([ x1 , y1+y2 ])
    
    return additive_shares

# ====

def genX(n):
    x = []
    for i in range(n):
        x.append(1 + i)
    return x

def coeff(t, secret): 
    # Randomly generate a coefficient array for a polynomial with degree t-1.
    coeff = [ random.randrange(0, field_size) for _ in range(t-1) ]
    coeff.insert(0, secret) # Add secret in the coeff as the constance of the polynomial.
    return coeff 

def polynom(x, coeff): 
    # Evaluates a polynomial in x with coefficient list
    coeff_num = list( range(0 , len(coeff)) )
    # print(coeff_num)

    poly = []
    for i in coeff_num:
        poly.append(coeff[i] * (x**i))
    # print(poly)

    return sum(poly)

def generateShares(n, t, secret):
    
    # secret not allow 非整數，secret not allow > PRIME
    secret = round(secret, 0)
    assert secret < PRIME, "PRIME must be larger than secret ! PRIME is {}, secret is {}." .format(PRIME, secret)

    cfs = coeff(t, secret)          # 產生隨機 t-1 多項式，其中 secret 隱藏在常數係數。( 有 t個座標點 可恢復 t-1 多項式 )
    x = genX(n)                     # 產生 n 個 x座標 ( 每個 secret 的 share 需要 相同x座標，才能計算 加法同態 )
    # print(cfs)
    # print(x)
    
    shares = []                     # 取得 多項式對應x座標的解，成為 n位 參與者的 share。
    for i in range(0, n):
        # shares.append([ x[i] , polynom(x[i], cfs) % PRIME ])
        shares.append([ x[i] , round(polynom(x[i], cfs), 1) % PRIME ])
    
    return shares 

# ====

'''
def reconstructSecret(shares): 
    
    # Combines shares using Lagranges interpolation.  
    sums = 0
    prod_arr = [] 
      
    for j in range(len(shares)): 
        xj, yj = shares[j][0],shares[j][1] 
        prod = Decimal(1) 
          
        for i in range(len(shares)): 
            xi = shares[i][0] 
            if i != j: 
                prod *= Decimal(Decimal(xi)/(xi-xj))          
        prod *= Decimal(yj) 
        sums += Decimal(prod) 

    return round(Decimal(sums),1)     
    #return int(round(Decimal(sums),0)) 
'''
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

        prod = (prod * yj) % PRIME
        sums = (sums) % PRIME + (prod) % PRIME

    # reconstruct = sums
    reconstruct = round( sums , 1 ) % PRIME

    return reconstruct

# ====

# Driver code  
if __name__ == '__main__': 
    
    print("\n====\n")
    
    # (n,t) sharing scheme 
    n,t = 11, 7

    # Phase I: Generation shares of secret

    secret = 100
    print('Original Secret:', secret)

    shares = generateShares(n, t, secret) 
    print('Shares:', *shares)

    print()

    # Phase II: Secret Reconstruction t-1
    pool = random.sample(shares, t-1) 
    print('Number of pooling:', len(pool) , ', Pooling shares:', *pool) 
    print("Reconstructed secret:", reconstructSecret(pool)) 

    print()

    # Phase II: Secret Reconstruction t
    pool = random.sample(shares, t) 
    print('Number of pooling:', len(pool) , ', Pooling shares:', *pool) 
    print("Reconstructed secret:", reconstructSecret(pool)) 

    print("\n====\n")

    # (n,t) sharing scheme 
    P1 = []
    P2 = []
    n,t = 2, 2

    # Phase I: Generation shares of secret 1

    secret = 55
    print('Original Secret 1:', secret) 
   
    shares = generateShares(n, t, secret) 
    print('Shares:', *shares)

    print()

    P1.append(shares[0])
    P2.append(shares[1])
    print('P1 share:', *P1)
    print('P2 share:', *P2)
 
    print()

    # Phase I: Generation shares of secret 2

    secret = 105
    print('Original Secret 2:', secret) 

    shares = generateShares(n, t, secret) 
    print('Shares:', *shares)
    
    print()
    
    P1.append(shares[1])
    P2.append(shares[0])
    print('P1 share:', *P1)
    print('P2 share:', *P2)

    print()

    # Phase II: Secret Additive Reconstruction
    additive_share = two_party_share_Addition(P1, P2)
    print('additive_share:', *additive_share)
    print("Reconstructed secret additive:", reconstructSecret(additive_share)) 

    print("\n====\n")
    
    # (n,t) sharing scheme 
    n,t = 3,3

    # Phase I: Generation shares of secret

    secret = 33.3
    print('Original Secret:', secret)

    shares = generateShares(n, t, secret) 
    print('Shares:', *shares)

    print()

    # Phase II: Secret Reconstruction t
    pool = random.sample(shares, t) 
    print('Number of pooling:', len(pool) , ', Pooling shares:', *pool) 
    print("Reconstructed secret:", reconstructSecret(pool)) 

    print("\n====\n")

    