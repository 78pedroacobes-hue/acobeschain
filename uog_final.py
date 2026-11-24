# -*- coding: utf-8 -*-
# UOG-FINAL — 54 features idénticas, Berry 60, OTOC/Loschmidt 40,
# ensemble estratificado por degeneración espectral
# LICENCIA: PROPIETARIA — TODOS LOS DERECHOS RESERVADOS
import numpy as np
from scipy.linalg import eigh
import warnings, json, time
from multiprocessing import Pool, cpu_count
warnings.filterwarnings("ignore")

I2=np.eye(2,dtype=complex); X=np.array([[0,1],[1,0]],dtype=complex)
Y=np.array([[0,-1j],[1j,0]],dtype=complex); Z=np.array([[1,0],[0,-1]],dtype=complex)
PAULIS=[I2,X,Y,Z]

def _expH(H,t):
    w,V=eigh(H); return (V*np.exp(-1j*w*t))@V.conj().T

def vN(v):
    s=np.linalg.svd(v.reshape(2,2),compute_uv=False); p=s[s>1e-15]**2
    return float(-np.sum(p*np.log2(p)))

def S_(r):
    e=np.linalg.eigvalsh(r).clip(1e-15); return float(-np.sum(e*np.log2(e)))

def g54(H):
    """54 features idénticas — sin recortes. Berry 60 pasos. OTOC/Loschmidt 40."""
    H=np.asarray(H,dtype=complex); N=4
    if not np.allclose(H,H.conj().T,atol=1e-10):
        H=(H+H.conj().T)/2
    vals,V=eigh(H)
    G={}
    v0=V[:,0]

    # básicos
    G['spectral_radius']=float(np.max(np.abs(vals)))
    d=np.abs(np.diff(np.sort(vals)))
    G['spectral_gap']=float(d.min()) if len(d) else 0.0
    G['trace_real']=float(np.trace(H).real)
    G['det_abs']=float(abs(np.linalg.det(H)))
    c=np.poly(H); acc=np.zeros_like(H)
    for k,co in enumerate(c): acc=acc+co*np.linalg.matrix_power(H,N-k)
    G['CH_residual']=float(np.linalg.norm(acc))

    # pseudo-hermiticidad
    eta=(V*np.exp(0.5*vals))@V.conj().T
    ev=np.linalg.eigvalsh(eta)
    G['eta_cond']=float(ev.max()/ev.min())

    # entrelazamiento
    G['entropy_max']=float(max(vN(V[:,i]) for i in range(4)))
    YY=np.kron(Y,Y)
    G['concurrence_max']=float(max(abs(np.vdot(V[:,i],YY@V[:,i].conj())) for i in range(4)))

    # ratios
    vv=np.sort(vals); sp=np.diff(vv)
    if len(sp)>=2:
        r=[min(sp[i],sp[i+1])/max(sp[i],sp[i+1]) for i in range(len(sp)-1)]
        G['r_ratio']=float(np.mean(r))
    else: G['r_ratio']=0.0

    # OTOC — 40 pasos (sin recorte)
    W=np.kron(Z,I2); Vo=np.kron(I2,Z); psi=np.zeros(4,dtype=complex); psi[0]=1
    ot=[]
    for t in np.linspace(0,5,40):
        U=_expH(H,t); Wt=U.conj().T@W@U
        ot.append(float(np.real(psi.conj()@Wt@Vo@Wt@Vo@psi)))
    G['OTOC_min']=float(min(ot)); G['OTOC_range']=float(max(ot)-min(ot))

    # Loschmidt — 40 pasos
    Hp=H+0.1*np.kron(X,X)
    le=[abs(psi.conj()@_expH(H,t).conj().T@_expH(Hp,t)@psi)**2 for t in np.linspace(0,5,40)]
    G['loschmidt_min']=float(min(le))

    # Krylov
    b=[]; prev=np.zeros(N,dtype=complex); cur=psi/np.linalg.norm(psi); bp=0.0
    for _ in range(8):
        w=H@cur-bp*prev; a=float(np.real(np.vdot(cur,w))); w=w-a*cur
        bc=float(np.linalg.norm(w))
        if bc<1e-14: break
        b.append(bc); prev,cur,bp=cur,w/bc,bc
    G['krylov_growth']=float(b[-1]/b[0]) if len(b)>1 else 0.0

    # entropía dinámica
    G['dyn_entropy_max']=float(max(vN(_expH(H,t)@psi) for t in np.linspace(0,5,15)))

    # IPR
    iprs=[float((np.abs(V[:,i])**4).sum()) for i in range(N)]
    G['IPR_max']=float(max(iprs)); G['IPR_min']=float(min(iprs)); G['IPR_mean']=float(np.mean(iprs))

    # Fubini
    Vp=(np.kron(X,Y)+np.kron(Y,X))/2; e=1e-3
    _,V0_=eigh(H); _,Vp_=eigh(H+e*Vp); _,Vm_=eigh(H-e*Vp)
    p0=V0_[:,0]; pp=Vp_[:,0]; pm=Vm_[:,0]; dp=(pp-pm)/(2*e)
    G['fubini_study']=float(np.real(np.vdot(dp,dp)-abs(np.vdot(p0,dp))**2))

    # Berry — 60 pasos (sin recorte)
    Vb=np.kron(X,Y); Vb=(Vb+Vb.conj().T)/2
    n=60; st=[]
    for th in np.linspace(0,2*np.pi,n,endpoint=False):
        Hm=np.cos(th)*H+np.sin(th)*Vb; Hm=(Hm+Hm.conj().T)/2
        st.append(eigh(Hm)[1][:,0])
    G['berry_phase']=float(sum(float(np.angle(np.vdot(st[i],st[(i+1)%n]))) for i in range(n)))

    # winding
    dd=[]
    for th in np.linspace(0,2*np.pi,n,endpoint=False):
        Hm=np.cos(th)*H+np.sin(th)*Vb; Hm=(Hm+Hm.conj().T)/2
        w=np.linalg.eigvalsh(Hm); dd.append(float(w[0]-w[1]))
    s=np.sign(dd); G['winding']=int((s[:-1]!=s[1:]).sum())

    # resolvent
    rn=[]
    for z in [0.1j,0.5+0.5j,1.0,2.0-0.5j]:
        try: rn.append(float(np.linalg.norm(np.linalg.inv(H-z*np.eye(N)))))
        except: rn.append(np.inf)
    G['resolvent_max']=float(max(rn))
    G['pseudo_density']=0.0

    # Lyapunov
    otv=np.array(ot); decay=otv[0]-otv.min()
    if decay<0.05: G['lyapunov']=0.0
    else:
        y=np.log(np.abs(1-otv)+1e-15); ts=np.linspace(0,5,40); m=np.isfinite(y)
        G['lyapunov']=float(np.polyfit(ts[m],y[m],1)[0]) if m.sum()>3 else 0.0

    # Bures, fidelidad
    p1=_expH(H,0.5)@psi; p2=_expH(H,1.0)@psi
    G['bures_sq']=float(2-2*np.sqrt(abs(np.vdot(p1,p2))**2))
    G['fidelity_t1']=float(abs(np.vdot(psi,_expH(H,1.0)@psi))**2)

    # información mutua, negatividad, discord
    M=v0.reshape(2,2); rA=M@M.conj().T; rB=M.conj().T@M
    G['mutual_info']=float(S_(rA)+S_(rB))
    rho=np.outer(v0,v0.conj())
    rpt=rho.reshape(2,2,2,2).transpose(0,3,2,1).reshape(4,4)
    er=np.linalg.eigvalsh(rpt)
    G['negativity']=float((np.abs(er).sum()-1)/2)
    G['discord_proxy']=float(min(S_(rA),S_(rB)))

    # complejidad, Fisher
    U=_expH(H,1.0)
    G['circuit_complexity']=float(np.linalg.norm(np.angle(np.linalg.eigvals(U))))
    plus=np.ones(4,dtype=complex)/2
    eH=float(np.real(np.vdot(plus,H@plus)))
    var=float(np.real(np.vdot(plus,H@H@plus))-eH**2)
    G['fisher_Q']=float(4*var)

    # conmutante y álgebra
    ad=np.zeros((N*N,N*N),dtype=complex)
    for i in range(N):
        for j in range(N):
            E=np.zeros((N,N),dtype=complex); E[i,j]=1
            ad[:,i*N+j]=(H@E-E@H).flatten()
    sd=np.linalg.svd(ad,compute_uv=False)
    G['commutant_dim']=int(N*N-(sd>1e-8).sum())
    pw=np.array([np.linalg.matrix_power(H,k).flatten() for k in range(N)]).T
    sa=np.linalg.svd(pw,compute_uv=False)
    G['algebra_dim']=int((sa>1e-8).sum())

    # geometría
    D=np.zeros((N,N))
    for i in range(N):
        for j in range(N): D[i,j]=1-abs(np.vdot(V[:,i],V[:,j]))**2
    off=D[D>1e-8]
    G['geom_diameter']=float(D.max())
    G['geom_mean']=float(off.mean()) if len(off) else 0.0

    # entropía espectral
    pv=np.abs(vals); pv=pv/pv.sum()
    G['spectral_entropy']=float(-np.sum(pv*np.log2(pv+1e-15)))

    # red
    A=np.abs(H); np.fill_diagonal(A,0)
    G['net_density']=float((A>1e-8).sum()/(N*(N-1)))

    # Rényi, Schmidt
    sv=np.linalg.svd(v0.reshape(2,2),compute_uv=False)
    p2_=sv**2; p2_=p2_[p2_>1e-15]
    G['renyi_2']=float(-np.log2(np.sum(p2_**2)))
    G['renyi_inf']=float(-np.log2(np.max(p2_)))
    G['purity_red']=float(np.real(np.trace(rA@rA)))
    G['schmidt_rank']=int((sv>1e-10).sum())
    G['schmidt_top1']=float(sv[0]) if len(sv) else 0.0
    e1=np.sort(np.linalg.eigvalsh(rA))[::-1]
    G['ent_spec_1']=float(e1[0])

    # arg det, trace_dist_pi
    G['arg_det_H']=float(np.angle(np.linalg.det(H)))
    Upi=_expH(H,np.pi); rho_pi=Upi@rho@Upi.conj().T
    G['trace_dist_pi']=float(0.5*np.sum(np.abs(np.linalg.eigvalsh(rho-rho_pi))))

    # spacing
    spn=sp/sp.mean() if len(sp)>0 else np.array([0.0])
    if len(spn)>2:
        llp=np.sum(np.log(np.exp(-spn)+1e-15))
        llw=np.sum(np.log((np.pi/2)*spn*np.exp(-np.pi*spn**2/4)+1e-15))
        G['spacing_LL_diff']=float(llw-llp)
    else: G['spacing_LL_diff']=0.0

    # level velocity, fidelity susceptibility
    w0,_=eigh(H); w1,_=eigh(H+e*Vp)
    G['level_vel_max']=float(np.max(np.abs((w1-w0)/e)))
    F=abs(np.vdot(Vp_[:,0],Vm_[:,0]))**2
    G['fidelity_suscept']=float(2*(1-F)/e**2)

    # QGT
    ps=V0_[:,0]
    _,Va=eigh(H+e*Vp); _,Vb_=eigh(H-e*Vp)
    d1=(Va[:,0]-Vb_[:,0])/(2*e)
    G['qgt_norm']=float(abs(np.vdot(d1,d1)-abs(np.vdot(ps,d1))**2))

    # Husimi, coherencia
    probs=np.real(np.diag(rho)); G['husimi_purity']=float(np.sum(probs**2))
    G['coh_l1']=float(np.sum(np.abs(rho))-np.sum(np.abs(np.diag(rho))))

    # asimetría Z
    Z4=np.kron(np.diag([1,-1]),np.eye(2))
    wZ,VZ=eigh(Z4); Uz=(VZ*np.exp(-1j*(np.pi/2)*wZ))@VZ.conj().T
    G['asymmetry_Z']=float(np.linalg.norm(rho-Uz@rho@Uz.conj().T))

    # Lorenz
    pp_=np.sort(np.abs(v0)**2)[::-1]
    cum=np.cumsum(pp_); xx=np.arange(1,len(pp_)+1)/len(pp_)
    G['lorenz_area']=float(np.trapezoid(cum,xx))

    # ETH
    G['eth_viol']=float(np.std(np.diag(H))/(abs(np.diag(H).mean())+1e-12))

    # operador como estado bipartito
    Hres=H.reshape(2,2,2,2).transpose(0,2,1,3).reshape(4,4)
    so=np.linalg.svd(Hres,compute_uv=False); po=so**2
    po=po[po>1e-15]; po=po/po.sum()
    G['op_entropy']=float(-np.sum(po*np.log2(po)))

    # clasificación espectral: degenerado o no
    min_gap=float(d.min()) if len(d) else 0.0
    G['_spec_type']='non-degenerate' if min_gap>1e-6 else 'degenerate'
    G['_min_gap']=min_gap

    return G

# ============ 12 FAMILIAS ============
def f_gue(rng):
    A=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4)); return (A+A.conj().T)/2
def f_nonH(rng):
    A=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4)); return A/np.linalg.norm(A)
def f_PT(rng):
    A=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4)); P=np.eye(4)[::-1]
    return A+P@A.conj()@P
def f_pauli(rng):
    c=rng.normal(size=16)+1j*rng.normal(size=16)
    M=sum(c[k]*np.kron(PAULIS[k//4],PAULIS[k%4]) for k in range(16))
    return (M+M.conj().T)/2
def f_hankel(rng):
    v=rng.normal(size=7); H=np.zeros((4,4))
    for i in range(4):
        for j in range(4): H[i,j]=v[i+j]
    return (H+H.T)/2
def f_toeplitz(rng):
    c=rng.normal(size=4); r=rng.normal(size=4)
    H=np.zeros((4,4))
    for i in range(4):
        for j in range(4): H[i,j]= c[j-i] if j>=i else r[i-j]
    return (H+H.T)/2
def f_sylvester(rng):
    return np.diag(rng.integers(-5,6,size=4).astype(float))
def f_laplacian(rng):
    W=rng.random((4,4)); W=(W+W.T)/2; np.fill_diagonal(W,0)
    return (np.diag(W.sum(axis=1))-W).astype(complex)
def f_adjacency(rng):
    A=(rng.random((4,4))>0.5).astype(float); A=(A+A.T)/2; np.fill_diagonal(A,0)
    return A.astype(complex)
def f_projection(rng):
    A=rng.normal(size=(4,2))+1j*rng.normal(size=(4,2))
    Q,_=np.linalg.qr(A); return Q@Q.conj().T
def f_density(rng):
    A=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4))
    rho=A@A.conj().T; return rho/np.trace(rho)
def f_sym_complex(rng):
    A=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4)); A=A+A.T
    return (A+A.conj().T)/2

FAMILIES=[("GUE",f_gue),("NonH",f_nonH),("PT",f_PT),("Pauli",f_pauli),
    ("Hankel",f_hankel),("Toeplitz",f_toeplitz),("Diagonal",f_sylvester),
    ("Laplacian",f_laplacian),("Adjacency",f_adjacency),
    ("Projection",f_projection),("Density",f_density),("SymComplex",f_sym_complex)]

def work(args):
    fam_idx,seed=args
    try:
        rng=np.random.default_rng(seed)
        M=FAMILIES[fam_idx][1](rng)
        return g54(M)
    except Exception:
        return None

if __name__=="__main__":
    N_PER_FAM=500
    N_FAM=len(FAMILIES)
    N_TOTAL=N_PER_FAM*N_FAM
    n_proc=max(1,cpu_count()-1)
    print(f"{N_FAM} familias × {N_PER_FAM} = {N_TOTAL} ops, {n_proc} procesos")
    print("Berry 60, OTOC 40, Loschmidt 40, 54 features sin recortes")
    args=[(fi,200000+fi*10000+s) for fi in range(N_FAM) for s in range(N_PER_FAM)]
    t0=time.time()
    results=[]
    with Pool(n_proc) as p:
        for i,r in enumerate(p.imap_unordered(work,args,chunksize=20)):
            if r is not None: results.append(r)
            if (i+1)%500==0:
                el=time.time()-t0; eta=el/(i+1)*(N_TOTAL-i-1)
                print(f"  {i+1}/{N_TOTAL}  ({el:.0f}s, ETA {eta:.0f}s)")
    print(f"Completado en {time.time()-t0:.0f}s. Válidos: {len(results)}")

    keys=[k for k in sorted(results[0].keys()) if not k.startswith('_')]
    ens={k:np.array([r[k] for r in results]) for k in keys}
    spec_types=[r['_spec_type'] for r in results]

    Psi=np.zeros((4,4),dtype=complex)
    Psi[0,0]=-1.5427; Psi[1,1]=1.6933; Psi[2,2]=1.0; Psi[3,3]=1.0
    Psi[0,2]=Psi[2,0]=0.5057; Psi[1,2]=Psi[2,1]=0.0759; Psi[2,3]=Psi[3,2]=0.5
    psi_g=g54(Psi)
    psi_type=psi_g['_spec_type']
    print(f"\nΨ tipo espectral: {psi_type}, min_gap={psi_g['_min_gap']:.6f}")

    # ESTRATIFICACIÓN
    idx_match=[i for i,t in enumerate(spec_types) if t==psi_type]
    print(f"Operadores del ensemble con tipo '{psi_type}': {len(idx_match)} / {len(results)}")

    def reportar(nombre, indices):
        print("\n"+"="*62); print(f"{nombre}  (n={len(indices)})"); print("="*62)
        print(f"{'feature':>22} {'PSI':>12} {'pct':>8} {'ext':>5}")
        print("-"*62)
        ext=[]
        for k in keys:
            arr=np.array([ens[k][i] for i in indices])
            if np.std(arr)<1e-12: continue
            pv=float(psi_g[k])
            pct=float((arr<pv).mean()*100)
            mk="***" if (pct<5 or pct>95) else ""
            if mk: ext.append((k,pv,pct))
            print(f"{k:>22} {pv:>12.6f} {pct:>7.2f}% {mk:>5}")
        print(f"\nExtremos: {len(ext)}/{len(keys)}")
        for k,pv,pct in ext:
            print(f"  {k:>22} = {pv:+.6f}  (pct {pct:.2f}%)")
        return ext

    ext_all=reportar("A) CONTRA TODO EL ENSEMBLE", list(range(len(results))))
    ext_match=reportar(f"B) CONTRA SOLO '{psi_type}'", idx_match)

    with open("uog_final_result.json","w") as f:
        json.dump({
            "n_total":N_TOTAL,"n_valid":len(results),"n_fam":N_FAM,
            "psi_type":psi_type,"n_match":len(idx_match),
            "ext_all":[(k,pv,pct) for k,pv,pct in ext_all],
            "ext_match":[(k,pv,pct) for k,pv,pct in ext_match],
            "total_features":len(keys)}, f, indent=2)
    print("\nGuardado: uog_final_result.json")
