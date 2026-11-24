# -*- coding: utf-8 -*-
# =============================================================================
#  UOG ENGINE v3 — 72 capas AUTOCONTENIDO
#  LICENCIA: PROPIETARIA — TODOS LOS DERECHOS RESERVADOS
# =============================================================================

import numpy as np
import hashlib, json, warnings
from scipy.linalg import expm, eigh
warnings.filterwarnings("ignore")
np.set_printoptions(precision=8, suppress=True, linewidth=180)

I2 = np.eye(2, dtype=complex)
X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]], dtype=complex)
Z = np.array([[1,0],[0,-1]], dtype=complex)


def vN(state, dims):
    M = state.reshape(dims)
    s = np.linalg.svd(M, compute_uv=False)
    p = s[s > 1e-15]**2
    return float(-np.sum(p * np.log2(p)))


def H2(p):
    p = np.clip(p, 1e-15, 1-1e-15)
    return -p*np.log2(p) - (1-p)*np.log2(1-p)


# =============================================================================
# CLASE BASE — 36 capas (UOG v2)
# =============================================================================
class UOG:
    def __init__(self, H, name="op", fast=False):
        self.H = np.asarray(H, dtype=complex)
        self.N = self.H.shape[0]
        self.name = name
        self.fast = fast
        self.G = {}
        self._hermitian = None
        self._vals = None
        self._vecs = None

    def _Hh(self):
        if self._hermitian is None:
            self._hermitian = bool(np.allclose(self.H, self.H.conj().T, atol=1e-10))
        return self.H if self._hermitian else (self.H + self.H.conj().T) / 2

    def _spec(self):
        if self._vals is None:
            Hh = self._Hh()
            if self._hermitian:
                self._vals, self._vecs = eigh(Hh)
            else:
                self._vals, self._vecs = np.linalg.eig(Hh)
                idx = np.argsort(self._vals.real)
                self._vals = self._vals[idx]
                self._vecs = self._vecs[:, idx]
        return self._vals, self._vecs

    def L01_hermiticity(self):
        self.G['hermitian'] = bool(self._Hh() is not None and self._hermitian)

    def L02_spectrum(self):
        v, _ = self._spec()
        self.G['spectral_radius'] = float(np.max(np.abs(v)))
        d = np.abs(np.diff(np.sort(v.real)))
        self.G['spectral_gap'] = float(d.min()) if len(d) else 0.0
        self.G['trace_real'] = float(np.trace(self.H).real)
        self.G['det_abs'] = float(abs(np.linalg.det(self.H)))

    def L03_cayley(self):
        c = np.poly(self._Hh())
        acc = np.zeros_like(self.H)
        for k, coef in enumerate(c):
            acc = acc + coef * np.linalg.matrix_power(self._Hh(), self.N - k)
        self.G['CH_residual'] = float(np.linalg.norm(acc))

    def L04_PT(self):
        if self.N not in (4,):
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
        v, _ = self._spec()
        r = v.real
        p = int((r > 1e-10).sum()); q = int((r < -1e-10).sum()); z = int((np.abs(r) <= 1e-10).sum())
        self.G['krein_signature'] = (p, q, z)

    def L06_pseudoH(self):
        eta = expm(0.5 * self._Hh())
        ev = np.linalg.eigvalsh(eta)
        self.G['pseudo_hermitian'] = bool(np.all(ev > 0))
        self.G['eta_cond'] = float(ev.max() / ev.min())

    def L07_EP(self):
        if self.N != 4 or self.fast:
            self.G['EP_found'] = None; return
        Hh = self._Hh()
        V = 1j * np.kron(X, Y)
        best_gap, best_cond, lam_best = 1e9, 0.0, 0.0
        for lam in np.linspace(0, 3, 300):
            Hl = Hh + lam * V
            w = np.sort_complex(np.linalg.eigvals(Hl))
            g = float(np.min(np.abs(np.diff(w))))
            if g < best_gap:
                best_gap, lam_best = g, lam
                try:
                    _, vr = np.linalg.eig(Hl)
                    best_cond = float(np.linalg.cond(vr))
                except Exception:
                    best_cond = np.inf
        self.G['EP_found'] = bool(best_gap < 1e-3 and best_cond > 1e3)
        self.G['EP_min_gap'] = best_gap
        self.G['EP_max_cond'] = best_cond
        self.G['EP_lambda'] = lam_best

    def L08_ent(self):
        if self.N != 4:
            self.G['entropy_max'] = None; return
        _, vecs = self._spec()
        S, C = [], []
        for i in range(4):
            v = vecs[:, i]
            S.append(vN(v, (2,2)))
            C.append(abs(np.vdot(v, np.kron(Y, Y) @ v.conj())))
        self.G['entropy_max'] = float(max(S))
        self.G['concurrence_max'] = float(max(C))

    def L09_stats(self):
        v, _ = self._spec()
        v = np.sort(v.real)
        sp = np.diff(v)
        if len(sp) < 2:
            self.G['r_ratio'] = None; return
        r = [min(sp[i], sp[i+1])/max(sp[i], sp[i+1]) for i in range(len(sp)-1)]
        self.G['r_ratio'] = float(np.mean(r))

    def L10_OTOC(self):
        if self.N != 4 or self.fast:
            self.G['OTOC_range'] = None; return
        Hh = self._Hh()
        W = np.kron(Z, I2); V = np.kron(I2, Z)
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        vals = []
        for t in np.linspace(0, 5, 40):
            U = expm(-1j * Hh * t)
            Wt = U.conj().T @ W @ U
            vals.append(float(np.real(psi.conj() @ Wt @ V @ Wt @ V @ psi)))
        self.G['OTOC_min'] = float(min(vals))
        self.G['OTOC_range'] = float(max(vals) - min(vals))

    def L11_loschmidt(self):
        if self.N != 4 or self.fast:
            self.G['loschmidt_min'] = None; return
        Hh = self._Hh()
        Hp = Hh + 0.1 * np.kron(X, X)
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        le = []
        for t in np.linspace(0, 5, 40):
            U = expm(-1j * Hh * t); Up = expm(-1j * Hp * t)
            le.append(float(abs(psi.conj() @ U.conj().T @ Up @ psi)**2))
        self.G['loschmidt_min'] = float(min(le))

    def L12_krylov(self):
        Hh = self._Hh()
        psi = np.zeros(self.N, dtype=complex); psi[0] = 1.0
        b, prev = [], np.zeros_like(psi)
        cur = psi / np.linalg.norm(psi); bp = 0.0
        for _ in range(min(8, self.N)):
            w = Hh @ cur - bp * prev
            a = float(np.real(np.vdot(cur, w)))
            w = w - a * cur
            bc = float(np.linalg.norm(w))
            if bc < 1e-14: break
            b.append(bc); prev, cur, bp = cur, w/bc, bc
        self.G['krylov_b'] = b
        self.G['krylov_growth'] = float(b[-1]/b[0]) if len(b) > 1 else 0.0

    def L13_dyn_ent(self):
        if self.N != 4 or self.fast: return
        Hh = self._Hh()
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        S = [vN(expm(-1j*Hh*t) @ psi, (2,2)) for t in np.linspace(0, 5, 20)]
        self.G['dyn_entropy_max'] = float(max(S))

    def L14_IPR(self):
        _, vecs = self._spec()
        iprs = [float((np.abs(vecs[:,i])**4).sum()) for i in range(self.N)]
        self.G['IPR_max'] = float(max(iprs))
        self.G['IPR_min'] = float(min(iprs))
        self.G['IPR_mean'] = float(np.mean(iprs))

    def L15_fractal(self):
        _, vecs = self._spec()
        v = vecs[:, 0]; p = np.abs(v)**2; p /= p.sum()
        Dq = {}
        for q in [-2, -1, 0, 2, 3]:
            Dq[q] = float((np.sum(p**q))**(1/(1-q)) / self.N)
        S = -np.sum(p * np.log(p + 1e-15))
        Dq[1] = float(np.exp(S) / self.N)
        self.G['fractal_Dq'] = Dq

    def L16_fubini(self):
        if self.fast or self.N < 4: return
        Hh = self._Hh()
        V = (np.kron(X, Y) + np.kron(Y, X)) / 2.0
        def gs(Hm):
            Hm = (Hm + Hm.conj().T) / 2
            return eigh(Hm)[1][:, 0]
        eps = 1e-3
        psi0 = gs(Hh); psip = gs(Hh + eps*V); psim = gs(Hh - eps*V)
        dpsi = (psip - psim) / (2*eps)
        self.G['fubini_study'] = float(np.real(np.vdot(dpsi, dpsi) - abs(np.vdot(psi0, dpsi))**2))

    def L17_berry(self):
        if self.fast or self.N < 4: return
        Hh = self._Hh()
        V = np.kron(X, Y); V = (V + V.conj().T) / 2
        n = 60
        states = []
        for th in np.linspace(0, 2*np.pi, n, endpoint=False):
            Hm = np.cos(th)*Hh + np.sin(th)*V
            Hm = (Hm + Hm.conj().T) / 2
            states.append(eigh(Hm)[1][:, 0])
        gamma = sum(float(np.angle(np.vdot(states[i], states[(i+1) % n]))) for i in range(n))
        self.G['berry_phase'] = float(gamma)
        self.G['berry_pi'] = bool(abs(abs(gamma) - np.pi) < 0.1)

    def L18_topology(self):
        if self.fast or self.N < 4: return
        Hh = self._Hh()
        V = np.kron(X, Y); V = (V + V.conj().T) / 2
        n = 60
        d = []
        for th in np.linspace(0, 2*np.pi, n, endpoint=False):
            Hm = np.cos(th)*Hh + np.sin(th)*V
            Hm = (Hm + Hm.conj().T) / 2
            w = np.linalg.eigvalsh(Hm)
            d.append(float(w[0] - w[1]))
        s = np.sign(d)
        self.G['winding'] = int((s[:-1] != s[1:]).sum())

    def L19_resolvent(self):
        Hh = self._Hh()
        norms = []
        for z in [0.1j, 0.5+0.5j, 1.0, 2.0-0.5j]:
            try:
                norms.append(float(np.linalg.norm(np.linalg.inv(Hh - z*np.eye(self.N)))))
            except Exception:
                norms.append(np.inf)
        self.G['resolvent_max'] = float(max(norms))

    def L20_pseudospec(self):
        if self.fast:
            self.G['pseudo_density'] = None; return
        Hh = self._Hh()
        eps, grid = 0.1, 25
        cnt = 0
        for x in np.linspace(-2, 2, grid):
            for y in np.linspace(-2, 2, grid):
                s = np.linalg.svd(Hh - (x+1j*y)*np.eye(self.N), compute_uv=False)
                if s.min() < eps: cnt += 1
        self.G['pseudo_density'] = float(cnt / (grid*grid))

    def L21_lyapunov(self):
        if self.N != 4 or self.fast:
            self.G['lyapunov'] = None; return
        Hh = self._Hh()
        W = np.kron(Z, I2); V = np.kron(I2, Z)
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        ts = np.linspace(0, 3, 25)
        vals = []
        for t in ts:
            U = expm(-1j*Hh*t); Wt = U.conj().T @ W @ U
            vals.append(float(np.real(psi.conj() @ Wt @ V @ Wt @ V @ psi)))
        vals = np.array(vals)
        decay = vals[0] - vals.min()
        if decay < 0.05:
            self.G['lyapunov'] = 0.0; self.G['chaotic'] = False; return
        y = np.log(np.abs(1 - vals) + 1e-15)
        m = np.isfinite(y)
        if m.sum() > 3:
            self.G['lyapunov'] = float(np.polyfit(ts[m], y[m], 1)[0])
        else:
            self.G['lyapunov'] = 0.0
        self.G['chaotic'] = bool(self.G['lyapunov'] > 0.1)

    def L22_bures(self):
        if self.N != 4: return
        Hh = self._Hh()
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        p1 = expm(-1j*Hh*0.5) @ psi
        p2 = expm(-1j*Hh*1.0) @ psi
        fid = abs(np.vdot(p1, p2))**2
        self.G['bures_sq'] = float(2 - 2*np.sqrt(fid))

    def L23_fidelity(self):
        if self.N != 4: return
        Hh = self._Hh()
        psi = np.zeros(4, dtype=complex); psi[0] = 1.0
        self.G['fidelity_t1'] = float(abs(np.vdot(psi, expm(-1j*Hh) @ psi))**2)

    def L24_mutual(self):
        if self.N != 4: return
        _, vecs = self._spec()
        M = vecs[:, 0].reshape(2,2)
        rA = M @ M.conj().T; rB = M.conj().T @ M
        def S(r):
            e = np.linalg.eigvalsh(r).clip(1e-15)
            return -np.sum(e * np.log2(e))
        self.G['mutual_info'] = float(S(rA) + S(rB))

    def L25_negativity(self):
        if self.N != 4: return
        _, vecs = self._spec()
        v = vecs[:, 0]
        rho = np.outer(v, v.conj())
        rho_pt = rho.reshape(2,2,2,2).transpose(0,3,2,1).reshape(4,4)
        e = np.linalg.eigvalsh(rho_pt)
        self.G['negativity'] = float((np.abs(e).sum() - 1) / 2)

    def L26_discord(self):
        if self.N != 4: return
        _, vecs = self._spec()
        M = vecs[:, 0].reshape(2,2)
        rA = M @ M.conj().T; rB = M.conj().T @ M
        def S(r):
            e = np.linalg.eigvalsh(r).clip(1e-15)
            return -np.sum(e * np.log2(e))
        self.G['discord_proxy'] = float(min(S(rA), S(rB)))

    def L27_circuit(self):
        Hh = self._Hh()
        U = expm(-1j * Hh)
        self.G['circuit_complexity'] = float(np.linalg.norm(np.angle(np.linalg.eigvals(U))))

    def L28_fisher(self):
        if self.N != 4: return
        Hh = self._Hh()
        plus = np.ones(4, dtype=complex) / 2.0
        eH = float(np.real(np.vdot(plus, Hh @ plus)))
        var = float(np.real(np.vdot(plus, Hh @ Hh @ plus)) - eH**2)
        self.G['fisher_Q'] = float(4 * var)

    def L29_commutant(self):
        N = self.N
        Hh = self._Hh()
        ad = np.zeros((N*N, N*N), dtype=complex)
        for i in range(N):
            for j in range(N):
                E = np.zeros((N,N), dtype=complex); E[i,j] = 1.0
                ad[:, i*N + j] = (Hh @ E - E @ Hh).flatten()
        s = np.linalg.svd(ad, compute_uv=False)
        rank = int((s > 1e-8).sum())
        self.G['commutant_dim'] = N*N - rank

    def L30_algebra(self):
        Hh = self._Hh()
        powers = np.array([np.linalg.matrix_power(Hh, k).flatten() for k in range(self.N)]).T
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
        if not self.G.get('hermitian', False):
            self.G['causal_type'] = 'non-hermitian'; return
        sig = self.G.get('krein_signature')
        if sig is None:
            self.G['causal_type'] = '?'; return
        p, q, z = sig
        if z > 0: self.G['causal_type'] = 'degenerate'
        elif q == 0: self.G['causal_type'] = 'euclidean'
        elif p == 1 or q == 1: self.G['causal_type'] = 'lorentzian'
        else: self.G['causal_type'] = 'ultra-hyperbolic'

    def L33_geometry(self):
        _, vecs = self._spec()
        N = self.N
        D = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                D[i,j] = 1 - abs(np.vdot(vecs[:,i], vecs[:,j]))**2
        off = D[D > 1e-8]
        self.G['geom_diameter'] = float(D.max())
        self.G['geom_mean'] = float(off.mean()) if len(off) else 0.0

    def L34_spec_ent(self):
        v, _ = self._spec()
        p = np.abs(v); p /= p.sum()
        self.G['spectral_entropy'] = float(-np.sum(p * np.log2(p + 1e-15)))

    def L35_network(self):
        Hh = self._Hh()
        N = self.N
        A = np.abs(Hh)
        np.fill_diagonal(A, 0.0)
        self.G['net_max_degree'] = float(A.sum(axis=1).max())
        self.G['net_density'] = float((A > 1e-8).sum() / (N*(N-1)))

    def genome(self):
        self.L01_hermiticity(); self._spec()
        self.L01_hermiticity()
        self.L02_spectrum(); self.L03_cayley()
        self.L04_PT(); self.L05_krein(); self.L06_pseudoH(); self.L07_EP()
        self.L08_ent(); self.L09_stats(); self.L10_OTOC()
        self.L11_loschmidt(); self.L12_krylov(); self.L13_dyn_ent()
        self.L14_IPR(); self.L15_fractal(); self.L16_fubini()
        self.L17_berry(); self.L18_topology(); self.L19_resolvent()
        self.L20_pseudospec(); self.L21_lyapunov(); self.L22_bures()
        self.L23_fidelity(); self.L24_mutual(); self.L25_negativity()
        self.L26_discord(); self.L27_circuit(); self.L28_fisher()
        self.L29_commutant(); self.L30_algebra(); self.L31_lie()
        self.L32_causal(); self.L33_geometry(); self.L34_spec_ent(); self.L35_network()
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
        if self.G.get('EP_found'): parts.append('EP')
        if self.G.get('berry_pi'): parts.append('Bpi')
        if self.G.get('chaotic'): parts.append('CHAOS')
        if (self.G.get('entropy_max') or 0) > 0.1: parts.append('E')
        parts.append(self.G.get('causal_type', '?')[:3].upper())
        parts.append(self.G.get('lie_algebra', '?'))
        return '-'.join(parts)


# =============================================================================
# UOG72 — 36 capas nuevas
# =============================================================================
class UOG72(UOG):
    def __init__(self, H, name="op", fast=False, beta=1.0):
        super().__init__(H, name, fast)
        self.beta = beta

    def _redA(self, v=None):
        if v is None:
            _, vecs = self._spec()
            v = vecs[:, 0]
        M = v.reshape(2, 2)
        return M @ M.conj().T

    def _schmidt(self):
        _, vecs = self._spec()
        v = vecs[:, 0]
        s = np.linalg.svd(v.reshape(2, 2), compute_uv=False)
        return s

    def _rho(self, v=None):
        if v is None:
            _, vecs = self._spec()
            v = vecs[:, 0]
        return np.outer(v, v.conj())

    def L36_renyi(self):
        s = self._schmidt(); p = s**2; p = p[p > 1e-15]
        self.G['renyi_2'] = float(-np.log2(np.sum(p**2)))
        self.G['renyi_3'] = float(-0.5*np.log2(np.sum(p**3)))
        self.G['renyi_inf'] = float(-np.log2(np.max(p)))

    def L37_tsallis(self):
        s = self._schmidt(); p = s**2; p = p[p > 1e-15]
        q = 2.0
        self.G['tsallis_q2'] = float((1 - np.sum(p**q)) / (q - 1))

    def L38_purity_red(self):
        rA = self._redA()
        self.G['purity_red'] = float(np.real(np.trace(rA @ rA)))

    def L39_schmidt(self):
        s = self._schmidt()
        rank = int((s > 1e-10).sum())
        self.G['schmidt_rank'] = rank
        self.G['schmidt_top1'] = float(s[0]) if len(s) else 0.0
        self.G['schmidt_top2'] = float(s[1]) if len(s) > 1 else 0.0

    def L40_ent_spectrum(self):
        rA = self._redA()
        e = np.sort(np.linalg.eigvalsh(rA))[::-1]
        self.G['ent_spec_1'] = float(e[0])
        self.G['ent_spec_2'] = float(e[1]) if len(e) > 1 else 0.0

    def L41_trace_dist(self):
        Hh = self._Hh()
        rho0 = self._rho()
        U = expm(-1j*Hh*np.pi)
        rho1 = U @ rho0 @ U.conj().T
        diff = rho0 - rho1
        self.G['trace_dist_pi'] = float(0.5*np.sum(np.abs(np.linalg.eigvalsh(diff))))

    def L42_HS_to_I(self):
        Hh = self._Hh()
        I = np.eye(self.N)
        self.G['hs_to_I'] = float(np.linalg.norm(Hh - I))

    def L43_arg_det(self):
        d = np.linalg.det(self._Hh())
        self.G['arg_det_H'] = float(np.angle(d))

    def L44_spacing_fit(self):
        v = np.sort(self._spec()[0].real)
        sp = np.diff(v)
        if len(sp) < 3:
            self.G['spacing_fit'] = 'too_few'; return
        sp = sp / sp.mean()
        def poisson_pdf(x): return np.exp(-x)
        def wignewigner'
        self.G['spacing_LL_diff'] = float(ll_w - ll_p)

    def L45_number_var(self):
        v = np.sort(self._spec()[0].real)
        L = 1.0
        cnt = 0
        for i in range(len(v)-1):
            if v[i+1] - v[i] < L: cnt += 1
        self.G['num_var_L1'] = float(cnt)

    def L46_spectral_form(self):
        v = self._spec()[0]
        tau = 1.0
        K = np.abs(np.sum(np.exp(2j*np.pi*tau*v)))**2 / len(v)
        self.G['spectral_form_tau1'] = float(K)

    def L47_level_velocity(self):
        if self.fast or self.N != 4:
            self.G['level_vel_max'] = None; return
        Hh = self._Hh()
        V = np.kron(X, Y); V = (V + V.conj().T)/2
        eps = 1e-3
        w0 = np.linalg.eigvalsh(Hh)
        w1 = np.linalg.eigvalsh(Hh + eps*V)
        self.G['level_vel_max'] = float(np.max(np.abs((w1-w0)/eps)))

    def L48_fidelity_suscept(self):
        if self.fast or self.N != 4:
            self.G['fidelity_suscept'] = None; return
        Hh = self._Hh()
        V = np.kron(X, Y); V = (V + V.conj().T)/2
        def gs(Hm):
            Hm = (Hm + Hm.conj().T)/2
            return eigh(Hm)[1][:, 0]
        psi0 = gs(Hh); eps = 1e-3
        p_plus  = gs(Hh + eps*V)
        p_minus = gs(Hh - eps*V)
        F = abs(np.vdot(p_plus, p_minus))**2
        self.G['fidelity_suscept'] = float(2*(1 - F)/eps**2)

    def L49_qgt(self):
        if self.fast or self.N != 4: return
        Hh = self._Hh()
        V1 = np.kron(X, Y); V1 = (V1 + V1.conj().T)/2
        V2 = np.kron(Y, X); V2 = (V2 + V2.conj().T)/2
        def gs(Hm):
            Hm = (Hm + Hm.conj().T)/2
            return eigh(Hm)[1][:, 0]
        eps = 1e-3
        psi = gs(Hh)
        d1 = (gs(Hh + eps*V1) - gs(Hh - eps*V1))/(2*eps)
        d2 = (gs(Hh + eps*V2) - gs(Hh - eps*V2))/(2*eps)
        Q11 = np.vdot(d1, d1) - abs(np.vdot(psi, d1))**2
        Q22 = np.vdot(d2, d2) - abs(np.vdot(psi, d2))**2
        Q12 = np.vdot(d1, d2) - np.vdot(d1, psi)*np.vdot(psi, d2)
        self.G['qgt_norm'] = float(abs(Q11) + abs(Q22))
        self.G['qgt_imag'] = float(np.imag(Q12))

    def L50_aQFI(self):
        rho = expm(-self.beta*self._Hh())
        rho = rho / np.trace(rho)
        ev, V = eigh(rho)
        eps = 1e-12
        denom = ev[:, None] + ev[None, :]
        denom[denom < eps] = eps
        dR = -self._Hh() @ rho - rho @ self._Hh() + 2*np.real(np.trace(self._Hh() @ rho))*rho
        dR_ev = V.conj().T @ dR @ V
        FQ = 0.0
        for i in range(self.N):
            for j in range(self.N):
                if i != j:
                    FQ += 2*abs(dR_ev[i, j])**2 / denom[i, j]
        self.G['aQFI'] = float(np.real(FQ))

    def L51_wigner_neg(self):
        if self.N != 4:
            self.G['wigner_neg'] = None; return
        rho = self._rho()
        pts = []
        for x1 in [0, 1]:
            for p1 in [0, 1]:
                for x2 in [0, 1]:
                    for p2 in [0, 1]:
                        U = np.kron(np.diag([1, (-1)**p1]), np.diag([1, (-1)**p2]))
                        A = np.zeros((4, 4), dtype=complex)
                        A[(x1*2+x2), (x1*2+x2)] = 1
                        W = U @ A @ U.conj().T
                        pts.append(float(np.real(np.trace(rho @ W))))
        W = np.array(pts)
        self.G['wigner_neg'] = float(-W[W < 0].sum())

    def L52_husimi_purity(self):
        rho = self._rho()
        probs = np.real(np.diag(rho))
        self.G['husimi_purity'] = float(np.sum(probs**2))

    def L53_mandel_Q(self):
        rho = self._rho()
        n = np.array([0, 0, 1, 1])
        navg = np.real(np.trace(rho @ np.diag(n)))
        n2avg = np.real(np.trace(rho @ np.diag(n**2)))
        var = n2avg - navg**2
        self.G['mandel_Q'] = float((var - navg) / (navg + 1e-12))

    def L54_antibunching(self):
        rho = self._rho()
        n = np.array([0, 0, 1, 1])
        a = np.diag(np.sqrt(n))
        num = np.real(np.trace(rho @ a.conj().T @ a.conj().T @ a @ a))
        den = (np.real(np.trace(rho @ a.conj().T @ a)))**2 + 1e-12
        self.G['g2_0'] = float(num / den)

    def L55_coh_l1(self):
        rho = self._rho()
        self.G['coh_l1'] = float(np.sum(np.abs(rho)) - np.sum(np.abs(np.diag(rho))))

    def L56_coh_relent(self):
        rho = self._rho()
        diag = np.diag(np.diag(rho))
        def S(r):
            e = np.linalg.eigvalsh(r).clip(1e-15)
            return -np.sum(e * np.log2(e))
        self.G['coh_relent'] = float(S(diag) - S(rho))

    def L57_coh_robust(self):
        rho = self._rho()
        diag = np.diag(np.diag(rho))
        self.G['coh_robust_lb'] = float(0.5 * np.linalg.norm(rho - diag, 'nuc'))

    def L58_asymmetry_Z(self):
        rho = self._rho()
        Z4 = np.kron(np.diag([1, -1]), np.eye(2))
        theta = np.pi/2
        U = expm(-1j*theta*Z4)
        self.G['asymmetry_Z'] = float(np.linalg.norm(rho - U @ rho @ U.conj().T))

    def L59_purity_full(self):
        rho = self._rho()
        self.G['purity_full'] = float(np.real(np.trace(rho @ rho)))

    def L60_linear_entropy(self):
        rho = self._rho()
        self.G['linear_entropy'] = float(1 - np.real(np.trace(rho @ rho)))

    def L61_lorenz(self):
        _, vecs = self._spec()
        v = vecs[:, 0]
        p = np.sort(np.abs(v)**2)[::-1]
        cum = np.cumsum(p)
        n = len(p)
        x = np.arange(1, n+1)/n
        area = np.trapezoid(cum, x)
        self.G['lorenz_area'] = float(area)

    def L62_eoF(self):
        s = self._schmidt()
        if len(s) < 4: self.G['eof_binary'] = 0.0; return
        c = abs(s[0]*s[1] - s[2]*s[3])
        self.G['eof_binary'] = float(H2((1 + np.sqrt(max(0, 1-c**2)))/2)) if c > 0 else 0.0

    def L63_squashed(self):
        rA = self._redA()
        e = np.linalg.eigvalsh(rA).clip(1e-15)
        self.G['squashed_proxy'] = float(-np.sum(e * np.log2(e)))

    def L64_qdeficit(self):
        rho = self._rho()
        M = rho.reshape(2, 2, 2, 2)
        rA = np.trace(M, axis1=1, axis2=3)
        rB = np.trace(M, axis1=0, axis2=2)
        def S(r):
            e = np.linalg.eigvalsh(r).clip(1e-15)
            return -np.sum(e * np.log2(e))
        self.G['qdeficit'] = float(S(rA) + S(rB))

    def L65_work_var(self):
        Hh = self._Hh()
        Hp = Hh + 0.1 * np.kron(X, X)
        rho = self._rho()
        dW = np.real(np.trace(rho @ (Hp - Hh)))
        dW2 = np.real(np.trace(rho @ (Hp - Hh) @ (Hp - Hh)))
        self.G['work_var'] = float(dW2 - dW**2)

    def L66_entropy_prod(self):
        Hh = self._Hh(); Hp = Hh + 0.1*np.kron(X, X)
        rho0 = self._rho()
        U = expm(-1j * Hh * 1.0)
        rho_t = U @ rho0 @ U.conj().T
        def S(r):
            e = np.linalg.eigvalsh(r).clip(1e-15)
            return -np.sum(e * np.log2(e))
        dS = S(rho_t) - S(rho0)
        Q = np.real(np.trace(rho_t @ (Hp - Hh)))
        self.G['entropy_prod'] = float(dS + self.beta * Q)

    def L67_nonMarkov(self):
        Hh = self._Hh()
        rho = self._rho()
        states = [expm(-1j*Hh*t) @ rho @ expm(-1j*Hh*t).conj().T for t in np.linspace(0, 3, 15)]
        max_growth = 0.0
        for i in range(1, len(states)-1):
            d1 = 0.5*np.sum(np.abs(np.linalg.eigvalsh(states[i] - states[i-1])))
            d2 = 0.5*np.sum(np.abs(np.linalg.eigvalsh(states[i+1] - states[i])))
            if d2 - d1 > max_growth: max_growth = d2 - d1
        self.G['nonmarkov_BLP'] = float(max_growth)

    def L68_coh_info(self):
        rho = self._rho()
        M = rho.reshape(2, 2, 2, 2)
        rB = np.trace(M, axis1=0, axis2=2)
        e = np.linalg.eigvalsh(rB).clip(1e-15)
        self.G['coherent_info'] = float(-np.sum(e * np.log2(e)))

    def L69_thermal_dist(self):
        rho = self._rho()
        rhoG = expm(-self.beta * self._Hh())
        rhoG = rhoG / np.trace(rhoG)
        self.G['thermal_dist'] = float(np.linalg.norm(rho - rhoG, 'fro'))

    def L70_ETH_viol(self):
        Hh = self._Hh()
        diag_own = np.real(np.diag(Hh))
        smooth = diag_own.mean()
        self.G['eth_viol'] = float(np.std(diag_own) / (abs(smooth) + 1e-12))

    def L71_op_ent(self):
        Hh = self._Hh()
        Hres = Hh.reshape(2, 2, 2, 2).transpose(0, 2, 1, 3).reshape(4, 4)
        s = np.linalg.svd(Hres, compute_uv=False)
        p = s**2; p = p[p > 1e-15]; p /= p.sum()
        self.G['op_entropy'] = float(-np.sum(p * np.log2(p)))

    def L72_op_rank(self):
        Hh = self._Hh()
        Hres = Hh.reshape(2, 2, 2, 2).transpose(0, 2, 1, 3).reshape(4, 4)
        s = np.linalg.svd(Hres, compute_uv=False)
        self.G['op_rank'] = int((s > 1e-10).sum())

    def genome72(self):
        super().genome()
        self.L36_renyi();           self.L37_tsallis();       self.L38_purity_red()
        self.L39_schmidt();         self.L40_ent_spectrum();  self.L41_trace_dist()
        self.L42_HS_to_I();         self.L43_arg_det();       self.L44_spacing_fit()
        self.L45_number_var();      self.L46_spectral_form(); self.L47_level_velocity()
        self.L48_fidelity_suscept();self.L49_qgt();           self.L50_aQFI()
        self.L51_wigner_neg();      self.L52_husimi_purity(); self.L53_mandel_Q()
        self.L54_antibunching();    self.L55_coh_l1();        self.L56_coh_relent()
        self.L57_coh_robust();      self.L58_asymmetry_Z();   self.L59_purity_full()
        self.L60_linear_entropy();  self.L61_lorenz();        self.L62_eoF()
        self.L63_squashed();        self.L64_qdeficit();      self.L65_work_var()
        self.L66_entropy_prod();    self.L67_nonMarkov();     self.L68_coh_info()
        self.L69_thermal_dist();    self.L70_ETH_viol();      self.L71_op_ent()
        self.L72_op_rank()
        return self.G


# =============================================================================
# DEMO
# =============================================================================
if __name__ == "__main__":

    Psi = np.zeros((4, 4), dtype=complex)
    Psi[0, 0] = -1.5427
    Psi[1, 1] =  1.6933
    Psi[2, 2] =  1.0
    Psi[3, 3] =  1.0
    Psi[0, 2] = Psi[2, 0] = 0.5057
    Psi[1, 2] = Psi[2, 1] = 0.0759
    Psi[2, 3] = Psi[3, 2] = 0.5

    u = UOG72(Psi, name="Psi")
    g = u.genome72()

    print("=" * 80)
    print("GENOMA COMPLETO — 72 CAPAS")
    print("=" * 80)

    claves = sorted(g.keys())
    for i, k in enumerate(claves, 1):
        v = g[k]
        if isinstance(v, float):
            print(f"  [{i:>2}] {k:>24} = {v:+.10f}")
        else:
            print(f"  [{i:>2}] {k:>24} = {v}")

    print(f"\nTotal de features: {len(g)}")
    print(f"GENOME ID = {u.genome_id()}")
    print(f"HASH      = {u.hash()}")
