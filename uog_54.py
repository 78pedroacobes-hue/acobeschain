# -*- coding: utf-8 -*-
# UOG-54 — 54 features discriminantes + ensemble + percentiles
# LICENCIA: PROPIETARIA — TODOS LOS DERECHOS RESERVADOS
import numpy as np
from scipy.linalg import expm, eigh
import warnings
warnings.filterwarnings("ignore")
np.set_printoptions(precision=8, suppress=True, linewidth=200)

I2=np.eye(2,dtype=complex); X=np.array([[0,1],[1,0]],dtype=complex)
Y=np.array([[0,-1j],[1j,0]],dtype=complex); Z=np.array([[1,0],[0,-1]],dtype=complex)

def vN(v):
    s=np.linalg.svd(v.reshape(2,2),compute_uv=False); p=s[s>1e-15]**2
    return float(-np.sum(p*np.log2(p)))

def S_(r):
    e=np.linalg.eigvalsh(r).clip(1e-15); return float(-np.sum(e*np.log2(e)))

class G54:
    def __init__(self,H):
        self.H=np.asarray(H,dtype=complex); self.N=self.H.shape[0]
        self.h=bool(np.allclose(self.H,self.H.conj().T,atol=1e-10))
        self.Hh=self.H if self.h else (self.H+self.H.conj().T)/2
        if self.h: self.vals,self.vecs=eigh(self.Hh)
        else:
            w,V=np.linalg.eig(self.Hh); i=np.argsort(w.real)
            self.vals=w[i]; self.vecs=V[:,i]
        self.G={}
    def calc(self):
        H=self.Hh; N=self.N; v=self.vals; V=self.vecs; G=self.G
        v0=V[:,0]
        # --- v2 base ---
        G['spectral_radius']=float(np.max(np.abs(v)))
        d=np.abs(np.diff(np.sort(v.real)))
        G['spectral_gap']=float(d.min()) if len(d) else 0.0
        G['trace_real']=float(np.trace(H).real)
        G['det_abs']=float(abs(np.linalg.det(H)))
        c=np.poly(H); acc=np.zeros_like(H)
        for k,co in enumerate(c): acc=acc+co*np.linalg.matrix_power(H,N-k)
        G['CH_residual']=float(np.linalg.norm(acc))
        eta=expm(0.5*H); ev=np.linalg.eigvalsh(eta)
        G['eta_cond']=float(ev.max()/ev.min())
        G['entropy_max']=float(max(vN(V[:,i]) for i in range(4)))
        G['concurrence_max']=float(max(abs(np.vdot(V[:,i],np.kron(Y,Y)@V[:,i].conj())) for i in range(4)))
        vv=np.sort(v.real); sp=np.diff(vv)
        if len(sp)>=2:
            r=[min(sp[i],sp[i+1])/max(sp[i],sp[i+1]) for i in range(len(sp)-1)]
            G['r_ratio']=float(np.mean(r))
        else: G['r_ratio']=0.0
        W=np.kron(Z,I2); Vo=np.kron(I2,Z); psi=np.zeros(4,dtype=complex); psi[0]=1
        ot=[]
        for t in np.linspace(0,5,15):
            U=expm(-1j*H*t); Wt=U.conj().T@W@U
            ot.append(float(np.real(psi.conj()@Wt@Vo@Wt@Vo@psi)))
        G['OTOC_min']=float(min(ot)); G['OTOC_range']=float(max(ot)-min(ot))
        Hp=H+0.1*np.kron(X,X)
        le=[abs(psi.conj()@expm(-1j*H*t).conj().T@expm(-1j*Hp*t)@psi)**2 for t in np.linspace(0,5,15)]
        G['loschmidt_min']=float(min(le))
        b=[]; prev=np.zeros(N,dtype=complex); cur=psi/np.linalg.norm(psi); bp=0.0
        for _ in range(8):
            w=H@cur-bp*prev; a=float(np.real(np.vdot(cur,w))); w=w-a*cur
            bc=float(np.linalg.norm(w))
            if bc<1e-14: break
            b.append(bc); prev,cur,bp=cur,w/bc,bc
        G['krylov_growth']=float(b[-1]/b[0]) if len(b)>1 else 0.0
        dyn=[vN(expm(-1j*H*t)@psi) for t in np.linspace(0,5,15)]
        G['dyn_entropy_max']=float(max(dyn))
        iprs=[(np.abs(V[:,i])**4).sum() for i in range(N)]
        G['IPR_max']=float(max(iprs)); G['IPR_min']=float(min(iprs)); G['IPR_mean']=float(np.mean(iprs))
        Vp=(np.kron(X,Y)+np.kron(Y,X))/2
        def gs(Hm):
            Hm=(Hm+Hm.conj().T)/2; return eigh(Hm)[1][:,0]
        e=1e-3; p0=gs(H); pp=gs(H+e*Vp); pm=gs(H-e*Vp); dp=(pp-pm)/(2*e)
        G['fubini_study']=float(np.real(np.vdot(dp,dp)-abs(np.vdot(p0,dp))**2))
        Vb=np.kron(X,Y); Vb=(Vb+Vb.conj().T)/2
        n=30; st=[]
        for th in np.linspace(0,2*np.pi,n,endpoint=False):
            Hm=np.cos(th)*H+np.sin(th)*Vb; Hm=(Hm+Hm.conj().T)/2
            st.append(eigh(Hm)[1][:,0])
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
            y=np.log(np.abs(1-otv)+1e-15); ts=np.linspace(0,5,15); m=np.isfinite(y)
            G['lyapunov']=float(np.polyfit(ts[m],y[m],1)[0]) if m.sum()>3 else 0.0
        p1=expm(-1j*H*0.5)@psi; p2=expm(-1j*H)@psi
        G['bures_sq']=float(2-2*np.sqrt(abs(np.vdot(p1,p2))**2))
        G['fidelity_t1']=float(abs(np.vdot(psi,expm(-1j*H)@psi))**2)
        M=v0.reshape(2,2); rA=M@M.conj().T; rB=M.conj().T@M
        G['mutual_info']=float(S_(rA)+S_(rB))
        rho=np.outer(v0,v0.conj())
        rpt=rho.reshape(2,2,2,2).transpose(0,3,2,1).reshape(4,4)
        er=np.linalg.eigvalsh(rpt)
        G['negativity']=float((np.abs(er).sum()-1)/2)
        G['discord_proxy']=float(min(S_(rA),S_(rB)))
        U=expm(-1j*H); G['circuit_complexity']=float(np.linalg.norm(np.angle(np.linalg.eigvals(U))))
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
        pv=np.abs(v); pv/=pv.sum()
        G['spectral_entropy']=float(-np.sum(pv*np.log2(pv+1e-15)))
        A=np.abs(H); np.fill_diagonal(A,0)
        G['net_density']=float((A>1e-8).sum()/(N*(N-1)))
        # --- v3 seleccionados (18) ---
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
        Upi=expm(-1j*H*np.pi); rho_pi=Upi@rho@Upi.conj().T
        G['trace_dist_pi']=float(0.5*np.sum(np.abs(np.linalg.eigvalsh(rho-rho_pi))))
        spn=sp/sp.mean() if len(sp)>0 else np.array([0.0])
        if len(spn)>2:
            llp=np.sum(np.log(np.exp(-spn)+1e-15))
            llw=np.sum(np.log((np.pi/2)*spn*np.exp(-np.pi*spn**2/4)+1e-15))
            G['spacing_LL_diff']=float(llw-llp)
        else: G['spacing_LL_diff']=0.0
        w0=np.linalg.eigvalsh(H); w1=np.linalg.eigvalsh(H+e*Vp)
        G['level_vel_max']=float(np.max(np.abs((w1-w0)/e)))
        F=abs(np.vdot(gs(H+e*Vp),gs(H-e*Vp)))**2
        G['fidelity_suscept']=float(2*(1-F)/e**2)
        V1=(np.kron(X,Y)+np.kron(Y,X))/2; V2=(np.kron(Y,X)+np.kron(X,Y))/2
        ps=gs(H)
        d1=(gs(H+e*V1)-gs(H-e*V1))/(2*e); d2=(gs(H+e*V2)-gs(H-e*V2))/(2*e)
        G['qgt_norm']=float(abs(np.vdot(d1,d1)-abs(np.vdot(ps,d1))**2)+abs(np.vdot(d2,d2)-abs(np.vdot(ps,d2))**2))
        probs=np.real(np.diag(rho)); G['husimi_purity']=float(np.sum(probs**2))
        G['coh_l1']=float(np.sum(np.abs(rho))-np.sum(np.abs(np.diag(rho))))
        Z4=np.kron(np.diag([1,-1]),np.eye(2)); Uz=expm(-1j*(np.pi/2)*Z4)
        G['asymmetry_Z']=float(np.linalg.norm(rho-Uz@rho@Uz.conj().T))
        pp_=np.sort(np.abs(v0)**2)[::-1]
        cum=np.cumsum(pp_); xx=np.arange(1,len(pp_)+1)/len(pp_)
        G['lorenz_area']=float(np.trapezoid(cum,xx))
        G['eth_viol']=float(np.std(np.diag(H))/(abs(np.diag(H).mean())+1e-12))
        Hres=H.reshape(2,2,2,2).transpose(0,2,1,3).reshape(4,4)
        so=np.linalg.svd(Hres,compute_uv=False); po=so**2
        po=po[po>1e-15]; po/=po.sum()
        G['op_entropy']=float(-np.sum(po*np.log2(po)))
        return G

def r_gue(n,rng):
    A=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)); return (A+A.conj().T)/2
def r_nonH(n,rng):
    A=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)); return A/np.linalg.norm(A)
def r_PT(n,rng):
    A=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n)); P=np.eye(n)[::-1]
    return A+P@A.conj()@P
def r_pauli(n,rng):
    c=rng.normal(size=16)+1j*rng.normal(size=16); P=[I2,X,Y,Z]
    M=sum(c[k]*np.kron(P[k//4],P[k%4]) for k in range(16))
    return (M+M.conj().T)/2

if __name__=="__main__":
    Psi=np.zeros((4,4),dtype=complex)
    Psi[0,0]=-1.5427; Psi[1,1]=1.6933; Psi[2,2]=1.0; Psi[3,3]=1.0
    Psi[0,2]=Psi[2,0]=0.5057; Psi[1,2]=Psi[2,1]=0.0759; Psi[2,3]=Psi[3,2]=0.5
    psi=G54(Psi).calc()
    keys=sorted(psi.keys())
    print("="*62); print(f"PSI — {len(keys)} features"); print("="*62)
    for i,k in enumerate(keys,1):
        v=psi[k]
        print(f"  [{i:>2}] {k:>22} = {v:+.8f}" if isinstance(v,float) else f"  [{i:>2}] {k:>22} = {v}")
    rng=np.random.default_rng(42)
    gens=[r_gue,r_nonH,r_PT,r_pauli]; N_ENS=300
    print(f"\nCorriendo ensemble de {N_ENS} operadores...")
    ens={k:[] for k in keys}
    for i in range(N_ENS):
        M=gens[i%4](4,rng)
        try:
            g=G54(M).calc()
            for k in keys: ens[k].append(g[k])
        except Exception: pass
    print("\n"+"="*62); print("PERCENTILES DE PSI EN EL ENSEMBLE"); print("="*62)
    print(f"{'feature':>22} {'PSI':>12} {'pct':>8} {'ext':>5}")
    print("-"*62)
    ext=[]
    for k in keys:
        arr=np.array(ens[k],dtype=float)
        if len(arr)==0 or np.std(arr)<1e-12: continue
        pv=float(psi[k]) if isinstance(psi[k],(int,float)) else 0.0
        pct=float((arr<pv).mean()*100)
        mark="***" if (pct<5 or pct>95) else ""
        if mark: ext.append((k,pv,pct))
        print(f"{k:>22} {pv:>12.6f} {pct:>7.2f}% {mark:>5}")
    print(f"\nFeatures en extremo (<5% o >95%): {len(ext)}/{len(keys)}")
    for k,pv,pct in ext:
        print(f"  {k:>22} = {pv:+.6f}  (pct {pct:.2f}%)")
