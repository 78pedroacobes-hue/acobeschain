# -*- coding: utf-8 -*-
# UOG-25K — Ensemble masivo 25.000 operadores con percentiles estabilizados
# LICENCIA: PROPIETARIA — TODOS LOS DERECHOS RESERVADOS
import numpy as np
from scipy.linalg import eigh
import warnings, json, time, os
from multiprocessing import Pool, cpu_count
warnings.filterwarnings("ignore")

I2=np.eye(2,dtype=complex); X=np.array([[0,1],[1,0]],dtype=complex)
Y=np.array([[0,-1j],[1j,0]],dtype=complex); Z=np.array([[1,0],[0,-1]],dtype=complex)

def _expH(H,t):
    w,V=eigh(H); return (V*np.exp(-1j*w*t))@V.conj().T

def vN(v):
    s=np.linalg.svd(v.reshape(2,2),compute_uv=False); p=s[s>1e-15]**2
    return float(-np.sum(p*np.log2(p)))

def S_(r):
    e=np.linalg.eigvalsh(r).clip(1e-15); return float(-np.sum(e*np.log2(e)))

def g54(H):
    H=np.asarray(H,dtype=complex); N=4
    if not np.allclose(H,H.conj().T,atol=1e-10):
        H=(H+H.conj().T)/2
    vals,V=eigh(H)
    G={}
    v0=V[:,0]
    G['spectral_radius']=float(np.max(np.abs(vals)))
    d=np.abs(np.diff(np.sort(vals)))
    G['spectral_gap']=float(d.min()) if len(d) else 0.0
    G['trace_real']=float(np.trace(H).real)
    G['det_abs']=float(abs(np.linalg.det(H)))
    c=np.poly(H); acc=np.zeros_like(H)
    for k,co in enumerate(c): acc=acc+co*np.linalg.matrix_power(H,N-k)
    G['CH_residual']=float(np.linalg.norm(acc))
    w_eta,V_eta=eigh(H); eta=(V_eta*np.exp(0.5*w_eta))@V_eta.conj().T
    ev=np.linalg.eigvalsh(eta); G['eta_cond']=float(ev.max()/ev.min())
    G['entropy_max']=float(max(vN(V[:,i]) for i in range(4)))
    YY=np.kron(Y,Y)
    G['concurrence_max']=float(max(abs(np.vdot(V[:,i],YY@V[:,i].conj())) for i in range(4)))
    vv=np.sort(vals); sp=np.diff(vv)
    if len(sp)>=2:
        r=[min(sp[i],sp[i+1])/max(sp[i],sp[i+1]) for i in range(len(sp)-1)]
        G['r_ratio']=float(np.mean(r))
    else: G['r_ratio']=0.0
    W=np.kron(Z,I2); Vo=np.kron(I2,Z); psi=np.zeros(4,dtype=complex); psi[0]=1
    ot=[]
    for t in np.linspace(0,5,10):
        U=_expH(H,t); Wt=U.conj().T@W@U
        ot.append(float(np.real(psi.conj()@Wt@Vo@Wt@Vo@psi)))
    G['OTOC_min']=float(min(ot)); G['OTOC_range']=float(max(ot)-min(ot))
    Hp=H+0.1*np.kron(X,X)
    le=[abs(psi.conj()@_expH(H,t).conj().T@_expH(Hp,t)@psi)**2 for t in np.linspace(0,5,10)]
    G['loschmidt_min']=float(min(le))
    b=[]; prev=np.zeros(N,dtype=complex); cur=psi/np.linalg.norm(psi); bp=0.0
    for _ in range(8):
        w=H@cur-bp*prev; a=float(np.real(np.vdot(cur,w))); w=w-a*cur
        bc=float(np.linalg.norm(w))
        if bc<1e-14: break
        b.append(bc); prev,cur,bp=cur,w/bc,bc
    G['krylov_growth']=float(b[-1]/b[0]) if len(b)>1 else 0.0
    dyn=[vN(_expH(H,t)@psi) for t in np.linspace(0,5,10)]
    G['dyn_entropy_max']=float(max(dyn))
    iprs=[float((np.abs(V[:,i])**4).sum()) for i in range(N)]
    G['IPR_max']=float(max(iprs)); G['IPR_min']=float(min(iprs)); G['IPR_mean']=float(np.mean(iprs))
    Vp=(np.kron(X,Y)+np.kron(Y,X))/2
    e=1e-3
    w0,_=eigh(H); w1,_=eigh(H+e*Vp); wm,_=eigh(H-e*Vp)
    # ground states via eigh
    _,Vp_=eigh(H+e*Vp); _,Vm_=eigh(H-e*Vp); _,V0_=eigh(H)
    p0=V0_[:,0]; pp=Vp_[:,0]; pm=Vm_[:,0]; dp=(pp-pm)/(2*e)
    G['fubini_study']=float(np.real(np.vdot(dp,dp)-abs(np.vdot(p0,dp))**2))
    Vb=np.kron(X,Y); Vb=(Vb+Vb.conj().T)/2
    n=24; st=[]
    for th in np.linspace(0,2*np.pi,n,endpoint=False):
        Hm=np.cos(th)*H+np.sin(th)*Vb; Hm=(Hm+Hm.conj().T)/2
        _,Vm2=eigh(Hm); st.append(Vm2[:,0])
    G['berry_phase']=float(sum(float(np.angle(np.vdot(st[i],st[(i+1)%n]))) for i in range(n)))
    dd=[]
    for th in np.linspace(0,2*np.pi,n,endpoint=False):
        Hm=np.cos(th)*H+np.sin(th)*Vb; Hm=(Hm+Hm.conj().T)/2
        w=np.linalg.eigvalsh(Hm); dd.append(float(w[0]-w[1]))
    s=np.sign(dd); G['winding']=int((s[:-1]!=s[1:]).sum())
    rn=[]
    for z in [0.1j,0.5+0.5j,1.0,2.0-0.5j]:
        try: rn.append(float(np.linalg.norm(np.linalg.inv(H-z*np.eye(N)))))
        except: rn.append(np.inf)
    G['resolvent_max']=float(max(rn)); G['pseudo_density']=0.0
    otv=np.array(ot); decay=otv[0]-otv.min()
    if decay<0.05: G['lyapunov']=0.0
    else:
        y=np.log(np.abs(1-otv)+1e-15); ts=np.linspace(0,5,10); m=np.isfinite(y)
        G['lyapunov']=float(np.polyfit(ts[m],y[m],1)[0]) if m.sum()>3 else 0.0
    p1=_expH(H,0.5)@psi; p2=_expH(H,1.0)@psi
    G['bures_sq']=float(2-2*np.sqrt(abs(np.vdot(p1,p2))**2))
    G['fidelity_t1']=float(abs(np.vdot(psi,_expH(H,1.0)@psi))**2)
    M=v0.reshape(2,2); rA=M@M.conj().T; rB=M.conj().T@M
    G['mutual_info']=float(S_(rA)+S_(rB))
    rho=np.outer(v0,v0.conj())
    rpt=rho.reshape(2,2,2,2).transpose(0,3,2,1).reshape(4,4)
    er=np.linalg.eigvalsh(rpt)
    G['negativity']=float((np.abs(er).sum()-1)/2)
    G['discord_proxy']=float(min(S_(rA),S_(rB)))
    U=_expH(H,1.0); G['circuit_complexity']=float(np.linalg.norm(np.angle(np.linalg.eigvals(U))))
    plus=np.ones(4,dtype=complex)/2
    eH=float(np.real(np.vdot(plus,H@plus)))
    var=float(np.real(np.vdot(plus,H@H@plus))-eH**2)
    G['fisher_Q']=float(4*var)
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
    D=np.zeros((N,N))
    for i in range(N):
        for j in range(N): D[i,j]=1-abs(np.vdot(V[:,i],V[:,j]))**2
    off=D[D>1e-8]
    G['geom_diameter']=float(D.max())
    G['geom_mean']=float(off.mean()) if len(off) else 0.0
    pv=np.abs(vals); pv=pv/pv.sum()
    G['spectral_entropy']=float(-np.sum(pv*np.log2(pv+1e-15)))
    A=np.abs(H); np.fill_diagonal(A,0)
    G['net_density']=float((A>1e-8).sum()/(N*(N-1)))
    s=np.linalg.svd(v0.reshape(2,2),compute_uv=False)
    p=s**2; p=p[p>1e-15]
    G['renyi_2']=float(-np.log2(np.sum(p**2)))
    G['renyi_inf']=float(-np.log2(np.max(p)))
    G['purity_red']=float(np.real(np.trace(rA@rA)))
    G['schmidt_rank']=int((s>1e-10).sum())
    G['schmidt_top1']=float(s[0]) if len(s) else 0.0
    e1=np.sort(np.linalg.eigvalsh(rA))[::-1]
    G['ent_spec_1']=float(e1[0])
    G['arg_det_H']=float(np.angle(np.linalg.det(H)))
    Upi=_expH(H,np.pi); rho_pi=Upi@rho@Upi.conj().T
    G['trace_dist_pi']=float(0.5*np.sum(np.abs(np.linalg.eigvalsh(rho-rho_pi))))
    spn=sp/sp.mean() if len(sp)>0 else np.array([0.0])
    if len(spn)>2:
        llp=np.sum(np.log(np.exp(-spn)+1e-15))
        llw=np.sum(np.log((np.pi/2)*spn*np.exp(-np.pi*spn**2/4)+1e-15))
        G['spacing_LL_diff']=float(llw-llp)
    else: G['spacing_LL_diff']=0.0
    G['level_vel_max']=float(np.max(np.abs((w1-w0)/e)))
    F=abs(np.vdot(Vp_[:,0],Vm_[:,0]))**2
    G['fidelity_suscept']=float(2*(1-F)/e**2)
    V1=(np.kron(X,Y)+np.kron(Y,X))/2; V2=V1
    ps=V0_[:,0]
    _,Va=eigh(H+e*V1); _,Vb_=eigh(H-e*V1)
    d1=(Va[:,0]-Vb_[:,0])/(2*e)
    G['qgt_norm']=float(abs(np.vdot(d1,d1)-abs(np.vdot(ps,d1))**2))
    probs=np.real(np.diag(rho)); G['husimi_purity']=float(np.sum(probs**2))
    G['coh_l1']=float(np.sum(np.abs(rho))-np.sum(np.abs(np.diag(rho))))
    Z4=np.kron(np.diag([1,-1]),np.eye(2))
    wZ,VZ=eigh(Z4); Uz=(VZ*np.exp(-1j*(np.pi/2)*wZ))@VZ.conj().T
    G['asymmetry_Z']=float(np.linalg.norm(rho-Uz@rho@Uz.conj().T))
    pp_=np.sort(np.abs(v0)**2)[::-1]
    cum=np.cumsum(pp_); xx=np.arange(1,len(pp_)+1)/len(pp_)
    G['lorenz_area']=float(np.trapezoid(cum,xx))
    G['eth_viol']=float(np.std(np.diag(H))/(abs(np.diag(H).mean())+1e-12))
    Hres=H.reshape(2,2,2,2).transpose(0,2,1,3).reshape(4,4)
    so=np.linalg.svd(Hres,compute_uv=False); po=so**2
    po=po[po>1e-15]; po=po/po.sum()
    G['op_entropy']=float(-np.sum(po*np.log2(po)))
    return G

def gen_op(args):
    kind,seed=args
    rng=np.random.default_rng(seed)
    if kind==0:
        A=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4)); return (A+A.conj().T)/2
    if kind==1:
        A=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4)); return A/np.linalg.norm(A)
    if kind==2:
        A=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4)); P=np.eye(4)[::-1]
        return A+P@A.conj()@P
    P=[I2,X,Y,Z]; c=rng.normal(size=16)+1j*rng.normal(size=16)
    M=sum(c[k]*np.kron(P[k//4],P[k%4]) for k in range(16))
    return (M+M.conj().T)/2

def work(args):
    kind,seed=args
    try:
        M=gen_op((kind,seed)); g=g54(M)
        return {k:float(v) if isinstance(v,(int,float,np.floating,np.integer)) else 0.0 for k,v in g.items()}
    except Exception:
        return None

if __name__=="__main__":
    N_TOTAL=25000
    n_proc=max(1,cpu_count()-1)
    print(f"Ensemble {N_TOTAL} operadores, {n_proc} procesos")
    args=[(i%4,1000+i) for i in range(N_TOTAL)]
    t0=time.time()
    results=[]
    with Pool(n_proc) as p:
        for i,r in enumerate(p.imap_unordered(work,args,chunksize=50)):
            if r is not None: results.append(r)
            if (i+1)%1000==0:
                el=time.time()-t0
                eta=el/(i+1)*(N_TOTAL-i-1)
                print(f"  {i+1}/{N_TOTAL}  ({el:.0f}s, ETA {eta:.0f}s)")
    print(f"Completado en {time.time()-t0:.0f}s. Válidos: {len(results)}")
    keys=sorted(results[0].keys())
    ens={k:np.array([r[k] for r in results]) for k in keys}
    # PSI
    Psi=np.zeros((4,4),dtype=complex)
    Psi[0,0]=-1.5427; Psi[1,1]=1.6933; Psi[2,2]=1.0; Psi[3,3]=1.0
    Psi[0,2]=Psi[2,0]=0.5057; Psi[1,2]=Psi[2,1]=0.0759; Psi[2,3]=Psi[3,2]=0.5
    psi_g=g54(Psi)
    print("\n"+"="*62); print("PERCENTILES PSI — 25.000 OPERADORES"); print("="*62)
    print(f"{'feature':>22} {'PSI':>12} {'pct':>8} {'ext':>5}")
    print("-"*62)
    ext=[]
    for k in keys:
        arr=ens[k]
        if np.std(arr)<1e-12: continue
        pv=float(psi_g[k])
        pct=float((arr<pv).mean()*100)
        mk="***" if (pct<5 or pct>95) else ""
        if mk: ext.append((k,pv,pct))
        print(f"{k:>22} {pv:>12.6f} {pct:>7.2f}% {mk:>5}")
    print(f"\nExtremos (<5% o >95%): {len(ext)}/{len(keys)}")
    for k,pv,pct in ext:
        print(f"  {k:>22} = {pv:+.6f}  (pct {pct:.2f}%)")
    with open("uog_25k_result.json","w") as f:
        json.dump({"n_total":N_TOTAL,"n_valid":len(results),
                   "extremos":[(k,pv,pct) for k,pv,pct in ext],
                   "total_features":len(keys)},
                  f,indent=2)
    print("\nGuardado: uog_25k_result.json")
