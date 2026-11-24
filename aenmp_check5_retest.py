import numpy as np
# Reusar funciones de v1.1 importando el archivo
import importlib.util
spec = importlib.util.spec_from_file_location("v11", "aenmp_atfb_p1_bell_diagonal_v1_1.py")
# No ejecutar el main de v1.1, solo copiar las funciones necesarias inline para retest rápido
# Copia mínima: usamos las mismas definiciones de v1.1
def bell_states():
    s = 1/np.sqrt(2)
    return [np.array([s,0,0,s], dtype=complex), np.array([s,0,0,-s], dtype=complex),
            np.array([0,s,s,0], dtype=complex), np.array([0,s,-s,0], dtype=complex)]
BELLS = bell_states()
PHI_PLUS = BELLS[0]
def rho_from_probs(p):
    p=np.array(p,float)
    rho=np.zeros((4,4),dtype=complex)
    for pi,psi in zip(p,BELLS):
        rho+=pi*np.outer(psi,psi.conj())
    return rho
def werner_probs(F):
    q=(1-F)/3.0
    return [F,q,q,q]
def build_cnot_16(c,t):
    U=np.zeros((16,16),dtype=complex)
    for inp in range(16):
        bits=[(inp>>(3-i))&1 for i in range(4)]
        ob=bits.copy()
        if bits[c]==1: ob[t]^=1
        oi=sum(b<<(3-i) for i,b in enumerate(ob))
        U[oi,inp]=1.0
    return U
U_ATFB=build_cnot_16(1,3)@build_cnot_16(0,2)
def atfb_p1(pp,pa):
    rho_in=np.kron(rho_from_probs(pp),rho_from_probs(pa))
    rp=U_ATFB@rho_in@U_ATFB.conj().T
    P=np.zeros((16,16),dtype=complex)
    for a in range(4):
        for b in [0,3]:
            P[a*4+b,a*4+b]=1.0
    ra=P@rp@P.conj().T
    rt=np.zeros((4,4),dtype=complex)
    for i in range(4):
        for j in range(4):
            rt[i,j]=sum(ra[i*4+k,j*4+k] for k in range(4))
    ps=np.trace(rt).real
    return ps, rp
def wilson(k,n,z=1.96):
    ph=k/n; d=1+z**2/n; c=(ph+z**2/(2*n))/d
    dl=z*np.sqrt((ph*(1-ph)+z**2/(4*n))/n)/d
    return ph,c-dl,c+dl
def mc(rp,N,seed):
    probs=np.real(np.diag(rp)); probs=np.maximum(probs,0); probs/=probs.sum()
    rng=np.random.default_rng(seed)
    s=rng.choice(16,size=N,p=probs)
    return sum(1 for x in s if ((x>>1)&1)==(x&1))

p_theo, rp = atfb_p1(werner_probs(0.60), werner_probs(0.90))
print(f"Teórico p={p_theo:.4f}")
print("Retest Check 5 con 20 semillas distintas, N=10000 cada una:")
hits=0
for seed in range(20):
    acc=mc(rp,10000,seed)
    ph,lo,hi=wilson(acc,10000)
    dentro=lo<=p_theo<=hi
    hits+=dentro
    print(f"seed {seed:2d}: p_hat={ph:.4f} Wilson=[{lo:.4f},{hi:.4f}] Dentro={dentro}")
print(f"\nCobertura: {hits}/20 = {hits/20*100:.0f}% - Esperado ~95% (19/20). Si da 18-20, el intervalo está bien.")
print("\nRetest con N=50000, semilla 123 (la que falló):")
acc=mc(rp,50000,123)
ph,lo,hi=wilson(acc,50000)
print(f"N=50000 seed 123: p_hat={ph:.4f} Wilson=[{lo:.4f},{hi:.4f}] Teórico={p_theo:.4f} Dentro={lo<=p_theo<=hi}")
