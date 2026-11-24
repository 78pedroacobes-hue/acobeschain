# -*- coding: utf-8 -*-
# =============================================================================
#  TACHYON ULTIMATE CLASSIFIER — Universal Operator Genome (UOG) v1
#  LICENCIA: PROPIETARIA — TODOS LOS DERECHOS RESERVADOS
# =============================================================================

import numpy as np
import scipy.linalg as spla
from scipy.linalg import expm, eigh, eigvalsh
import hashlib, json, warnings
warnings.filterwarnings("ignore")
np.set_printoptions(precision=8, suppress=True, linewidth=180)

I2 = np.eye(2, dtype=complex)
X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]], dtype=complex)
Z = np.array([[1,0],[0,-1]], dtype=complex)
PAULIS = [I2, X, Y, Z]

def vN(state, dims):
    dA, dB = dims
    M = state.reshape(dA, dB)
    s = np.linalg.svd(M, compute_uv=False)
    p = s[s > 1e-15]**2
    return float(-np.sum(p * np.log2(p)))

class UOG:
    def __init__(self, H, name="op", fast=False):
        self.H = np.asarray(H, dtype=complex)
        self.N = self.H.shape[0]
        self.name = name
        self.fast = fast
        self.G = {}

    def L01_hermiticity(self):
        h = np.allclose(self.H, self.H.conj().T, atol=1e-10)
        self.G['hermitian'] = bool(h)
        self.Hh = self.H if h else (self.H + self.H.conj().T) / 2

    def L02_spectrum(self):
        if self.G['hermitian']:
            self.vals, self.vecs = eigh(self.Hh)
        else:
            self.vals, self.vecs = np.linalg.eig(self.H)
        self.G['spectral_radius'] = float(np.max(np.abs(self.vals)))
        d = np.abs(np.diff(np.sort(self.vals.real)))
        self.G['spectral_gap'] = float(d.min()) if len(d) else 0.0
        self.G['trace_real'] = float(np.trace(self.H).real)
        self.G['det_abs'] = float(abs(np.linalg.det(self.H)))

    def L03_cayley_hamilton(self):
        c = np.poly(self.H)
        acc = np.zeros_like(self.H)
        for k, coef in enumerate(c):
            acc = acc + coef * np.linalg.matrix_power(self.H, self.N - k)
        self.G['CH_residual'] = float(np.linalg.norm(acc))

    def L04_PT(self):
        if self.N != 4:
            self.G['PT_symmetry'] = None; return
        Ps = {
            'swap': np.array([[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]], dtype=complex),
            'ZZ':   np.kron(Z, Z),
            'XX':   np.kron(X, X),
            'YY':   np.kron(Y, Y),
        }
        errs = {k: float(np.linalg.norm(P @ self.H.conj() @ P - self.H)) for k, P in Ps.items()}
        self.G['PT_errors'] = errs
        self.G['PT_symmetry'] = bool(min(errs.values()) < 1e-8)
        self.G['PT_best'] = min(errs, key=errs.get)

    def L05_krein(self):
        if not self.G['hermitian']:
            self.G['krein_signature'] = None; return
        v = self.vals.real
        p = int((v > 1e-10).sum()); q = int((v < -1e-10).sum()); z = int((np.abs(v) <= 1e-10).sum())
        self.G['krein_signature'] = (p, q, z)

    def L06_pseudo_hermitian(self):
        if not self.G['hermitian']:
            self.G['pseudo_hermitian'] = False; return
        eta = expm(0.5 * self.Hh)
        ev = np.linalg.eigvalsh(eta)
        self.G['pseudo_hermitian'] = bool(np.all(ev > 0))
        self.G['eta_cond'] = float(ev.max() / ev.min())

    def L07_EP(self):
        if self.N != 4 or self.fast:
            self.G['EP_max_cond'] = None; return
        V = 1j * np.kron(X, Y)
        max_c, min_g, lam_c = 0.0, 1e9, 0.0
        for lam in np.linspace(0, 2, 40):
            Hl = self.Hh + lam * V
            w = np.sort_complex(np.linalg.eigvals(Hl))
            g = np.min(np.abs(np.diff(w)))
            if g < min_g: min_g = g
            c = np.linalg.cond(np.linalg.eig(Hl)[1])
            if c > max_c: max_c, lam_c = c, lam
        self.G['EP_max_cond'] = float(max_c)
        self.G['EP_lambda'] = float(lam_c)
        self.G['EP_min_gap'] = float(min_g)

    def L08_entanglement(self):
        if self.N != 4:
            self.G['entropy_max'] = None; return
        S, C = [], []
        for i in range(4):
            v = self.vecs[:, i]
            S.append(vN(v, (2,2)))
            C.append(abs(np.vdot(v, np.kron(Y, Y) @ v.conj())))
        self.G['entropy_max'] = float(max(S))
        self.G['concurrence_max'] = float(max(C))

    def L09_spectral_stats(self):
        v = np.sort(self.vals.real)
        sp = np.diff(v)
        if len(sp) < 2:
            self.G['r_ratio'] = None; return
        r = [min(sp[i], sp[i+1])/max(sp[i], sp[i+1]) for i in range(len(sp)-1)]
        self.G['r_ratio'] = float(np.mean(r))

    def L10_OTOC(self):
        if self.N != 4 or self.fast:
            self.G['OTOC_range'] = None; return
        W = np.kron(Z, I2); V = np.kron(I2, Z)
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        vals = []
        for t in np.linspace(0, 5, 30):
            U = expm(-1j * self.Hh * t)
            Wt = U.conj().T @ W @ U
            vals.append(np.real(psi.conj() @ Wt @ V @ Wt @ V @ psi))
        self.G['OTOC_min'] = float(np.min(vals))
        self.G['OTOC_range'] = float(np.max(vals) - np.min(vals))

    def L11_loschmidt(self):
        if self.N != 4 or self.fast:
            self.G['loschmidt_min'] = None; return
        Hp = self.Hh + 0.1 * np.kron(X, X)
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        le = []
        for t in np.linspace(0, 5, 30):
            U = expm(-1j * self.Hh * t); Up = expm(-1j * Hp * t)
            le.append(abs(psi.conj() @ U.conj().T @ Up @ psi)**2)
        self.G['loschmidt_min'] = float(np.min(le))

    def L12_krylov(self):
        psi = np.zeros(self.N, dtype=complex); psi[0] = 1.0
        b, prev = [], np.zeros_like(psi)
        cur = psi / np.linalg.norm(psi); bp = 0.0
        for _ in range(8):
            w = self.Hh @ cur - bp * prev
            a = np.real(np.vdot(cur, w))
            w = w - a * cur
            bc = np.linalg.norm(w)
            if bc < 1e-14: break
            b.append(float(bc)); prev, cur, bp = cur, w/bc, bc
        self.G['krylov_b'] = b
        self.G['krylov_growth'] = float(b[-1]/b[0]) if len(b) > 1 else 0.0

    def L13_dynamical_entropy(self):
        if self.N != 4 or self.fast: return
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        S = [vN(expm(-1j*self.Hh*t) @ psi, (2,2)) for t in np.linspace(0,5,20)]
        self.G['dyn_entropy_max'] = float(max(S))

    def L14_IPR(self):
        iprs = [float((np.abs(self.vecs[:,i])**4).sum()) for i in range(self.N)]
        self.G['IPR_max'] = float(max(iprs))
        self.G['IPR_min'] = float(min(iprs))
        self.G['IPR_mean'] = float(np.mean(iprs))

    def L15_fractal_dim(self):
        v = self.vecs[:, 0]; p = np.abs(v)**2; p /= p.sum()
        Dq = {}
        for q in [-2, -1, 0, 2, 3]:
            if q == 1: continue
            Dq[q] = float((np.sum(p**q))**(1/(1-q)) / self.N)
        S = -np.sum(p * np.log(p + 1e-15))
        Dq[1] = float(np.exp(S) / self.N)
        self.G['fractal_Dq'] = Dq

    def L16_fubini_study(self):
        if self.fast: return
        V = 1j * (np.kron(X, Y) - np.kron(Y, X)) / 2
        def gs(Hm):
            Hm = (Hm + Hm.conj().T) / 2
            return eigh(Hm)[1][:, 0]
        eps = 1e-3
        psi0 = gs(self.Hh); psip = gs(self.Hh + eps*V); psim = gs(self.Hh - eps*V)
        dpsi = (psip - psim) / (2*eps)
        self.G['fubini_study'] = float(np.real(np.vdot(dpsi, dpsi) - abs(np.vdot(psi0, dpsi))**2))

    def L17_berry(self):
        if self.fast: return
        V = 1j * np.kron(X, Y)
        n = 40
        states = []
        for th in np.linspace(0, 2*np.pi, n, endpoint=False):
            Hm = np.cos(th)*self.Hh + np.sin(th)*V
            Hm = (Hm + Hm.conj().T) / 2
            states.append(eigh(Hm)[1][:, 0])
        gamma = sum(np.angle(np.vdot(states[i], states[(i+1) % n])) for i in range(n))
        self.G['berry_phase'] = float(gamma)

    def L18_topology(self):
        if self.fast: return
        V = 1j * np.kron(X, Y)
        n = 40
        d = []
        for th in np.linspace(0, 2*np.pi, n, endpoint=False):
            Hm = np.cos(th)*self.Hh + np.sin(th)*V
            Hm = (Hm + Hm.conj().T) / 2
            w = np.linalg.eigvalsh(Hm)
            d.append(w[0] - w[1])
        s = np.sign(d)
        self.G['winding'] = int((s[:-1] != s[1:]).sum())

    def L19_resolvent(self):
        norms = []
        for z in [0.1j, 0.5+0.5j, 1.0, 2.0-0.5j]:
            try:
                norms.append(float(np.linalg.norm(np.linalg.inv(self.Hh - z*np.eye(self.N)))))
            except: norms.append(np.inf)
        self.G['resolvent_max'] = float(max(norms))

    def L20_pseudospectrum(self):
        if self.fast: self.G['pseudo_density'] = None; return
        eps, grid = 0.1, 20
        cnt = 0
        for x in np.linspace(-2, 2, grid):
            for y in np.linspace(-2, 2, grid):
                s = np.linalg.svd(self.Hh - (x+1j*y)*np.eye(self.N), compute_uv=False)
                if s.min() < eps: cnt += 1
        self.G['pseudo_density'] = float(cnt / (grid*grid))

    def L21_lyapunov(self):
        if self.N != 4 or self.fast:
            self.G['lyapunov'] = None; return
        W = np.kron(Z, I2); V = np.kron(I2, Z)
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        ts = np.linspace(0, 1.5, 15)
        vals = []
        for t in ts:
            U = expm(-1j*self.Hh*t); Wt = U.conj().T @ W @ U
            vals.append(np.real(psi.conj() @ Wt @ V @ Wt @ V @ psi))
        y = np.log(np.abs(1 - np.array(vals)) + 1e-15)
        m = np.isfinite(y)
        if m.sum() > 3:
            try: self.G['lyapunov'] = float(np.polyfit(ts[m], y[m], 1)[0])
            except: self.G['lyapunov'] = 0.0
        else: self.G['lyapunov'] = 0.0

    def L22_bures(self):
        if self.N != 4: return
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        p1 = expm(-1j*self.Hh*0.5) @ psi
        p2 = expm(-1j*self.Hh*1.0) @ psi
        fid = abs(np.vdot(p1, p2))**2
        self.G['bures_sq'] = float(2 - 2*np.sqrt(fid))

    def L23_fidelity(self):
        if self.N != 4: return
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        self.G['fidelity_t1'] = float(abs(np.vdot(psi, expm(-1j*self.Hh) @ psi))**2)

    def L24_mutual_info(self):
        if self.N != 4: return
        M = self.vecs[:, 0].reshape(2,2)
        rA = M @ M.conj().T; rB = M.conj().T @ M
        def S(r):
            e = np.linalg.eigvalsh(r).clip(1e-15)
            return -np.sum(e * np.log2(e))
        self.G['mutual_info'] = float(S(rA) + S(rB))

    def L25_negativity(self):
        if self.N != 4: return
        v = self.vecs[:, 0]
        rho = np.outer(v, v.conj())
        rho_pt = rho.reshape(2,2,2,2).transpose(0,3,2,1).reshape(4,4)
        e = np.linalg.eigvalsh(rho_pt)
        self.G['negativity'] = float((np.abs(e).sum() - 1) / 2)

    def L26_discord(self):
        if self.N != 4: return
        M = self.vecs[:, 0].reshape(2,2)
        rA = M @ M.conj().T; rB = M.conj().T @ M
        def S(r):
            e = np.linalg.eigvalsh(r).clip(1e-15)
            return -np.sum(e * np.log2(e))
        self.G['discord_proxy'] = float(min(S(rA), S(rB)))

    def L27_circuit_complexity(self):
        U = expm(-1j * self.Hh)
        self.G['circuit_complexity'] = float(np.linalg.norm(np.angle(np.linalg.eigvals(U))))

    def L28_fisher(self):
        if self.N != 4: return
        v = self.vecs[:, 0]
        eH = np.real(np.vdot(v, self.Hh @ v))
        var = np.real(np.vdot(v, self.Hh @ self.Hh @ v)) - eH**2
        self.G['fisher_Q'] = float(4 * var)

    def L29_hidden_symmetries(self):
        N = self.N
        ad = np.zeros((N*N, N*N), dtype=complex)
        for i in range(N):
            for j in range(N):
                E = np.zeros((N,N), dtype=complex); E[i,j] = 1.0
                ad[:, i*N + j] = (self.Hh @ E - E @ self.Hh).flatten()
        s = np.linalg.svd(ad, compute_uv=False)
        rank = int((s > 1e-8).sum())
        self.G['commutant_dim'] = N*N - rank

    def L30_generated_algebra(self):
        powers = np.array([np.linalg.matrix_power(self.Hh, k).flatten() for k in range(self.N)]).T
        s = np.linalg.svd(powers, compute_uv=False)
        self.G['algebra_dim'] = int((s > 1e-8).sum())

    def L31_lie(self):
        cd = self.G.get('commutant_dim')
        N = self.N
        if cd is None: self.G['lie_algebra'] = 'unknown'
        elif cd == N: self.G['lie_algebra'] = 'u1^N'
        elif cd == N*N: self.G['lie_algebra'] = f'u({N})'
        else: self.G['lie_algebra'] = f'dim{cd}'

    def L32_causal(self):
        if not self.G['hermitian']:
            self.G['causal_type'] = 'non-hermitian'; return
        p, q, z = self.G['krein_signature']
        if z > 0: self.G['causal_type'] = 'degenerate'
        elif q == 0: self.G['causal_type'] = 'euclidean'
        elif p == 1 or q == 1: self.G['causal_type'] = 'lorentzian'
        else: self.G['causal_type'] = 'ultra-hyperbolic'

    def L33_geometry(self):
        N = self.N
        D = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                D[i,j] = 1 - abs(np.vdot(self.vecs[:,i], self.vecs[:,j]))**2
        off = D[D > 1e-8]
        self.G['geom_diameter'] = float(D.max())
        self.G['geom_mean'] = float(off.mean()) if len(off) else 0.0

    def L34_spectral_entropy(self):
        p = np.abs(self.vals); p /= p.sum()
        self.G['spectral_entropy'] = float(-np.sum(p * np.log2(p + 1e-15)))

    def L35_network(self):
        N = self.N
        A = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i != j:
                    A[i,j] = abs(self.vecs[:,i].conj() @ self.Hh @ self.vecs[:,j])
        self.G['net_max_degree'] = float(A.sum(axis=1).max())
        self.G['net_density'] = float((A > 1e-8).sum() / (N*(N-1)))

    def genome(self):
        self.L01_hermiticity(); self.L02_spectrum(); self.L03_cayley_hamilton()
        self.L04_PT(); self.L05_krein(); self.L06_pseudo_hermitian(); self.L07_EP()
        self.L08_entanglement(); self.L09_spectral_stats(); self.L10_OTOC()
        self.L11_loschmidt(); self.L12_krylov(); self.L13_dynamical_entropy()
        self.L14_IPR(); self.L15_fractal_dim(); self.L16_fubini_study()
        self.L17_berry(); self.L18_topology(); self.L19_resolvent()
        self.L20_pseudospectrum(); self.L21_lyapunov(); self.L22_bures()
        self.L23_fidelity(); self.L24_mutual_info(); self.L25_negativity()
        self.L26_discord(); self.L27_circuit_complexity(); self.L28_fisher()
        self.L29_hidden_symmetries(); self.L30_generated_algebra()
        self.L31_lie(); self.L32_causal(); self.L33_geometry()
        self.L34_spectral_entropy(); self.L35_network()
        return self.G

    def hash(self):
        def d(o):
            if isinstance(o, complex): return [o.real, o.imag]
            if isinstance(o, np.integer): return int(o)
            if isinstance(o, np.floating): return float(o)
            if isinstance(o, np.ndarray): return o.tolist()
            if isinstance(o, tuple): return list(o)
            return str(o)
        s = json.dumps(self.G, default=d, sort_keys=True)
        return hashlib.sha256(s.encode()).hexdigest()[:16]

    def genome_id(self):
        parts = []
        sig = self.G.get('krein_signature')
        if sig: parts.append(f"{sig[0]}-{sig[1]}-{sig[2]}")
        if self.G.get('hermitian'): parts.append('H')
        if self.G.get('pseudo_hermitian'): parts.append('PH')
        if self.G.get('PT_symmetry'): parts.append('PT')
        if (self.G.get('EP_max_cond') or 0) > 50: parts.append('EP')
        if (self.G.get('entropy_max') or 0) > 0.1: parts.append('E')
        parts.append(self.G.get('causal_type', '?')[:3].upper())
        parts.append(self.G.get('lie_algebra', '?'))
        return '-'.join(parts)


# =============================================================================
# DEMO: Psi original
# =============================================================================
if __name__ == "__main__":

    print("=" * 80)
    print("DEMO: OPERADOR PSI ORIGINAL")
    print("=" * 80)

    Psi = np.zeros((4,4), dtype=complex)
    Psi[0,0] = -1.5427
    Psi[1,1] =  1.6933
    Psi[2,2] =  1.0
    Psi[3,3] =  1.0
    Psi[0,2] = Psi[2,0] = 0.5057
    Psi[1,2] = Psi[2,1] = 0.0759
    Psi[2,3] = Psi[3,2] = 0.5

    u = UOG(Psi, name="Psi_original")
    g = u.genome()

    for k, v in g.items():
        print(f"  {k:>22} = {v}")

    print(f"\n  GENOME ID  = {u.genome_id()}")
    print(f"  HASH       = {u.hash()}")

    # =========================================================
    # ENSEMBLE
    # =========================================================
    print("\n" + "=" * 80)
    print("ENSEMBLE: 1000 OPERADORES ALEATORIOS")
    print("=" * 80)

    rng = np.random.default_rng(42)
    genomes = []
    ids = []

    def rand_gue(n):
        A = rng.normal(size=(n,n)) + 1j*rng.normal(size=(n,n))
        return (A + A.conj().T) / 2

    def rand_nonH(n):
        A = rng.normal(size=(n,n)) + 1j*rng.normal(size=(n,n))
        return A / np.linalg.norm(A)

    def rand_PT(n):
        A = rng.normal(size=(n,n)) + 1j*rng.normal(size=(n,n))
        P = np.eye(n)[::-1]
        return A + P @ A.conj() @ P

    def rand_pauli(n):
        c = rng.normal(size=16) + 1j*rng.normal(size=16)
        M = sum(c[k] * np.kron(PAULIS[k//4], PAULIS[k%4]) for k in range(16))
        return (M + M.conj().T) / 2

    gens = [rand_gue, rand_nonH, rand_PT, rand_pauli]
    labels = ['GUE','nonH','PT','Pauli']

    for i in range(1000):
        f = gens[i % 4]
        M = f(4)
        u = UOG(M, fast=True)
        u.genome()
        genomes.append(u.G)
        ids.append(u.genome_id())

    from collections import Counter
    cnt = Counter(ids)
    print(f"\nFamilias de genoma encontradas: {len(cnt)}")
    print("\nTop 15:")
    for gid, n in cnt.most_common(15):
        print(f"  {n:>4}  {gid}")

    with open("uog_ensemble.json", "w") as f:
        json.dump({"families": dict(cnt), "total": len(ids)}, f, indent=2)

    print("\nGuardado: uog_ensemble.json")
