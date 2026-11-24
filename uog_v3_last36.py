# -*- coding: utf-8 -*-
# =============================================================================
#  UOG v3 — SOLO CAPAS 36-72 (36 features nuevas)
#  LICENCIA: PROPIETARIA — TODOS LOS DERECHOS RESERVADOS
# =============================================================================

import numpy as np
import hashlib, json, warnings
from scipy.linalg import expm, eigh
warnings.filterwarnings("ignore")
np.set_printoptions(precision=10, suppress=True, linewidth=200)

I2 = np.eye(2, dtype=complex)
X  = np.array([[0,1],[1,0]], dtype=complex)
Y  = np.array([[0,-1j],[1j,0]], dtype=complex)
Z  = np.array([[1,0],[0,-1]], dtype=complex)


def H2(p):
    p = np.clip(p, 1e-15, 1-1e-15)
    return -p*np.log2(p) - (1-p)*np.log2(1-p)


class UOG_last36:
    def __init__(self, H, name="op", beta=1.0):
        self.H = np.asarray(H, dtype=complex)
        self.N = self.H.shape[0]
        self.name = name
        self.beta = beta
        self.G = {}
        self._hermitian = bool(np.allclose(self.H, self.H.conj().T, atol=1e-10))
        self.Hh = self.H if self._hermitian else (self.H + self.H.conj().T) / 2
        if self._hermitian:
            self.vals, self.vecs = eigh(self.Hh)
        else:
            w, V = np.linalg.eig(self.Hh)
            idx = np.argsort(w.real)
            self.vals = w[idx]
            self.vecs = V[:, idx]

    def _redA(self, v=None):
        if v is None:
            v = self.vecs[:, 0]
        M = v.reshape(2, 2)
        return M @ M.conj().T

    def _schmidt(self):
        v = self.vecs[:, 0]
        return np.linalg.svd(v.reshape(2, 2), compute_uv=False)

    def _rho(self, v=None):
        if v is None:
            v = self.vecs[:, 0]
        return np.outer(v, v.conj())

    # ===================== 36-40 ENTROPÍAS =====================
    def L36_renyi(self):
        s = self._schmidt(); p = s**2; p = p[p > 1e-15]
        self.G['renyi_2']   = float(-np.log2(np.sum(p**2)))
        self.G['renyi_3']   = float(-0.5*np.log2(np.sum(p**3)))
        self.G['renyi_inf'] = float(-np.log2(np.max(p)))

    def L37_tsallis(self):
        s = self._schmidt(); p = s**2; p = p[p > 1e-15]
        self.G['tsallis_q2'] = float((1 - np.sum(p**2)) / 1.0)

    def L38_purity_red(self):
        rA = self._redA()
        self.G['purity_red'] = float(np.real(np.trace(rA @ rA)))

    def L39_schmidt(self):
        s = self._schmidt()
        self.G['schmidt_rank'] = int((s > 1e-10).sum())
        self.G['schmidt_top1'] = float(s[0]) if len(s) else 0.0
        self.G['schmidt_top2'] = float(s[1]) if len(s) > 1 else 0.0

    def L40_ent_spectrum(self):
        e = np.sort(np.linalg.eigvalsh(self._redA()))[::-1]
        self.G['ent_spec_1'] = float(e[0])
        self.G['ent_spec_2'] = float(e[1]) if len(e) > 1 else 0.0

    # ===================== 41-46 ESPECTRAL FINO =====================
    def L41_trace_dist(self):
        rho0 = self._rho()
        U = expm(-1j*self.Hh*np.pi)
        rho1 = U @ rho0 @ U.conj().T
        self.G['trace_dist_pi'] = float(0.5*np.sum(np.abs(np.linalg.eigvalsh(rho0 - rho1))))

    def L42_HS_to_I(self):
        self.G['hs_to_I'] = float(np.linalg.norm(self.Hh - np.eye(self.N)))

    def L43_arg_det(self):
        self.G['arg_det_H'] = float(np.angle(np.linalg.det(self.Hh)))

    def L44_spacing_fit(self):
        v = np.sort(self.vals.real); sp = np.diff(v)
        if len(sp) < 3:
            self.G['spacing_fit'] = 'too_few'; return
        sp = sp / sp.mean()
        ll_p = np.sum(np.log(np.exp(-sp) + 1e-15))
        ll_w = np.sum(np.log((np.pi/2)*sp*np.exp(-np.pi*sp**2/4) + 1e-15))
        self.G['spacing_fit'] = 'poisson' if ll_p > ll_w else 'wigner'
        self.G['spacing_LL_diff'] = float(ll_w - ll_p)

    def L45_number_var(self):
        v = np.sort(self.vals.real)
        self.G['num_var_L1'] = float(sum(1 for i in range(len(v)-1) if v[i+1]-v[i] < 1.0))

    def L46_spectral_form(self):
        v = self.vals
        K = np.abs(np.sum(np.exp(2j*np.pi*v)))**2 / len(v)
        self.G['spectral_form_tau1'] = float(K)

    # ===================== 47-50 GEOMETRÍA =====================
    def L47_level_velocity(self):
        V = np.kron(X, Y); V = (V + V.conj().T)/2
        eps = 1e-3
        w0 = np.linalg.eigvalsh(self.Hh)
        w1 = np.linalg.eigvalsh(self.Hh + eps*V)
        self.G['level_vel_max'] = float(np.max(np.abs((w1-w0)/eps)))

    def L48_fidelity_suscept(self):
        V = np.kron(X, Y); V = (V + V.conj().T)/2
        def gs(Hm):
            Hm = (Hm + Hm.conj().T)/2
            return eigh(Hm)[1][:, 0]
        eps = 1e-3
        F = abs(np.vdot(gs(self.Hh + eps*V), gs(self.Hh - eps*V)))**2
        self.G['fidelity_suscept'] = float(2*(1 - F)/eps**2)

    def L49_qgt(self):
        V1 = np.kron(X, Y); V1 = (V1 + V1.conj().T)/2
        V2 = np.kron(Y, X); V2 = (V2 + V2.conj().T)/2
        def gs(Hm):
            Hm = (Hm + Hm.conj().T)/2
            return eigh(Hm)[1][:, 0]
        eps = 1e-3
        psi = gs(self.Hh)
        d1 = (gs(self.Hh + eps*V1) - gs(self.Hh - eps*V1))/(2*eps)
        d2 = (gs(self.Hh + eps*V2) - gs(self.Hh - eps*V2))/(2*eps)
        Q11 = np.vdot(d1, d1) - abs(np.vdot(psi, d1))**2
        Q22 = np.vdot(d2, d2) - abs(np.vdot(psi, d2))**2
        Q12 = np.vdot(d1, d2) - np.vdot(d1, psi)*np.vdot(psi, d2)
        self.G['qgt_norm'] = float(abs(Q11) + abs(Q22))
        self.G['qgt_imag'] = float(np.imag(Q12))

    def L50_aQFI(self):
        rho = expm(-self.beta*self.Hh); rho = rho / np.trace(rho)
        ev, V = eigh(rho)
        denom = ev[:, None] + ev[None, :]
        denom[denom < 1e-12] = 1e-12
        dR = -self.Hh @ rho - rho @ self.Hh + 2*np.real(np.trace(self.Hh @ rho))*rho
        dR_ev = V.conj().T @ dR @ V
        FQ = 0.0
        for i in range(self.N):
            for j in range(self.N):
                if i != j:
                    FQ += 2*abs(dR_ev[i, j])**2 / denom[i, j]
        self.G['aQFI'] = float(np.real(FQ))

    # ===================== 51-54 CUÁNTICA NO CLÁSICA =====================
    def L51_wigner_neg(self):
        rho = self._rho()
        pts = []
        for x1 in [0,1]:
            for p1 in [0,1]:
                for x2 in [0,1]:
                    for p2 in [0,1]:
                        U = np.kron(np.diag([1,(-1)**p1]), np.diag([1,(-1)**p2]))
                        A = np.zeros((4,4), dtype=complex)
                        A[x1*2+x2, x1*2+x2] = 1
                        W = U @ A @ U.conj().T
                        pts.append(float(np.real(np.trace(rho @ W))))
        W = np.array(pts)
        self.G['wigner_neg'] = float(-W[W < 0].sum())

    def L52_husimi_purity(self):
        probs = np.real(np.diag(self._rho()))
        self.G['husimi_purity'] = float(np.sum(probs**2))

    def L53_mandel_Q(self):
        rho = self._rho()
        n = np.array([0,0,1,1])
        navg = np.real(np.trace(rho @ np.diag(n)))
        n2 = np.real(np.trace(rho @ np.diag(n**2)))
        self.G['mandel_Q'] = float(((n2 - navg**2) - navg) / (navg + 1e-12))

    def L54_antibunching(self):
        rho = self._rho()
        n = np.array([0,0,1,1])
        a = np.diag(np.sqrt(n))
        num = np.real(np.trace(rho @ a.conj().T @ a.conj().T @ a @ a))
        den = (np.real(np.trace(rho @ a.conj().T @ a)))**2 + 1e-12
        self.G['g2_0'] = float(num / den)

    # ===================== 55-58 COHERENCIA =====================
    def L55_coh_l1(self):
        rho = self._rho()
        self.G['coh_l1'] = float(np.sum(np.abs(rho)) - np.sum(np.abs(np.diag(rho))))

    def L56_coh_relent(self):
        rho = self._rho(); diag = np.diag(np.diag(rho))
        def S(r):
            e = np.linalg.eigvalsh(r).clip(1e-15)
            return -np.sum(e * np.log2(e))
        self.G['coh_relent'] = float(S(diag) - S(rho))

    def L57_coh_robust(self):
        rho = self._rho(); diag = np.diag(np.diag(rho))
        self.G['coh_robust_lb'] = float(0.5*np.linalg.norm(rho - diag, 'nuc'))

    def L58_asymmetry_Z(self):
        rho = self._rho()
        Z4 = np.kron(np.diag([1,-1]), np.eye(2))
        U = expm(-1j*(np.pi/2)*Z4)
        self.G['asymmetry_Z'] = float(np.linalg.norm(rho - U @ rho @ U.conj().T))

    # ===================== 59-64 INFORMACIÓN =====================
    def L59_purity_full(self):
        rho = self._rho()
        self.G['purity_full'] = float(np.real(np.trace(rho @ rho)))

    def L60_linear_entropy(self):
        rho = self._rho()
        self.G['linear_entropy'] = float(1 - np.real(np.trace(rho @ rho)))

    def L61_lorenz(self):
        v = self.vecs[:, 0]
        p = np.sort(np.abs(v)**2)[::-1]
        cum = np.cumsum(p)
        x = np.arange(1, len(p)+1)/len(p)
        self.G['lorenz_area'] = float(np.trapezoid(cum, x))

    def L62_eoF(self):
        s = self._schmidt()
        if len(s) < 4:
            self.G['eof_binary'] = 0.0; return
        c = abs(s[0]*s[1] - s[2]*s[3])
        self.G['eof_binary'] = float(H2((1 + np.sqrt(max(0, 1-c**2)))/2)) if c > 0 else 0.0

    def L63_squashed(self):
        e = np.linalg.eigvalsh(self._redA()).clip(1e-15)
        self.G['squashed_proxy'] = float(-np.sum(e * np.log2(e)))

    def L64_qdeficit(self):
        rho = self._rho()
        M = rho.reshape(2,2,2,2)
        rA = np.trace(M, axis1=1, axis2=3)
        rB = np.trace(M, axis1=0, axis2=2)
        def S(r):
            e = np.linalg.eigvalsh(r).clip(1e-15)
            return -np.sum(e * np.log2(e))
        self.G['qdeficit'] = float(S(rA) + S(rB))

    # ===================== 65-70 TERMODINÁMICA =====================
    def L65_work_var(self):
        Hp = self.Hh + 0.1*np.kron(X, X)
        rho = self._rho()
        dW  = np.real(np.trace(rho @ (Hp - self.Hh)))
        dW2 = np.real(np.trace(rho @ (Hp - self.Hh) @ (Hp - self.Hh)))
        self.G['work_var'] = float(dW2 - dW**2)

    def L66_entropy_prod(self):
        Hp = self.Hh + 0.1*np.kron(X, X)
        rho0 = self._rho()
        U = expm(-1j*self.Hh)
        rho_t = U @ rho0 @ U.conj().T
        def S(r):
            e = np.linalg.eigvalsh(r).clip(1e-15)
            return -np.sum(e * np.log2(e))
        dS = S(rho_t) - S(rho0)
        Q  = np.real(np.trace(rho_t @ (Hp - self.Hh)))
        self.G['entropy_prod'] = float(dS + self.beta * Q)

    def L67_nonMarkov(self):
        rho = self._rho()
        states = [expm(-1j*self.Hh*t) @ rho @ expm(-1j*self.Hh*t).conj().T
                  for t in np.linspace(0, 3, 15)]
        mg = 0.0
        for i in range(1, len(states)-1):
            d1 = 0.5*np.sum(np.abs(np.linalg.eigvalsh(states[i] - states[i-1])))
            d2 = 0.5*np.sum(np.abs(np.linalg.eigvalsh(states[i+1] - states[i])))
            if d2 - d1 > mg: mg = d2 - d1
        self.G['nonmarkov_BLP'] = float(mg)

    def L68_coh_info(self):
        rho = self._rho()
        M = rho.reshape(2,2,2,2)
        rB = np.trace(M, axis1=0, axis2=2)
        e = np.linalg.eigvalsh(rB).clip(1e-15)
        self.G['coherent_info'] = float(-np.sum(e * np.log2(e)))

    def L69_thermal_dist(self):
        rho = self._rho()
        rhoG = expm(-self.beta*self.Hh); rhoG = rhoG / np.trace(rhoG)
        self.G['thermal_dist'] = float(np.linalg.norm(rho - rhoG, 'fro'))

    def L70_ETH_viol(self):
        diag_own = np.real(np.diag(self.Hh))
        self.G['eth_viol'] = float(np.std(diag_own) / (abs(diag_own.mean()) + 1e-12))

    # ===================== 71-72 OPERADOR COMO ESTADO =====================
    def L71_op_ent(self):
        Hres = self.Hh.reshape(2,2,2,2).transpose(0,2,1,3).reshape(4,4)
        s = np.linalg.svd(Hres, compute_uv=False)
        p = s**2; p = p[p > 1e-15]; p /= p.sum()
        self.G['op_entropy'] = float(-np.sum(p * np.log2(p)))

    def L72_op_rank(self):
        Hres = self.Hh.reshape(2,2,2,2).transpose(0,2,1,3).reshape(4,4)
        s = np.linalg.svd(Hres, compute_uv=False)
        self.G['op_rank'] = int((s > 1e-10).sum())

    def run(self):
        self.L36_renyi();            self.L37_tsallis();      self.L38_purity_red()
        self.L39_schmidt();          self.L40_ent_spectrum(); self.L41_trace_dist()
        self.L42_HS_to_I();          self.L43_arg_det();      self.L44_spacing_fit()
        self.L45_number_var();       self.L46_spectral_form();self.L47_level_velocity()
        self.L48_fidelity_suscept(); self.L49_qgt();          self.L50_aQFI()
        self.L51_wigner_neg();       self.L52_husimi_purity();self.L53_mandel_Q()
        self.L54_antibunching();     self.L55_coh_l1();       self.L56_coh_relent()
        self.L57_coh_robust();       self.L58_asymmetry_Z();  self.L59_purity_full()
        self.L60_linear_entropy();   self.L61_lorenz();       self.L62_eoF()
        self.L63_squashed();         self.L64_qdeficit();     self.L65_work_var()
        self.L66_entropy_prod();     self.L67_nonMarkov();    self.L68_coh_info()
        self.L69_thermal_dist();     self.L70_ETH_viol();     self.L71_op_ent()
        self.L72_op_rank()
        return self.G

    def hash(self):
        def d(o):
            if isinstance(o, complex): return [o.real, o.imag]
            if isinstance(o, np.integer): return int(o)
            if isinstance(o, np.floating): return float(o)
            if isinstance(o, np.ndarray): return o.tolist()
            if isinstance(o, tuple): return list(o)
            return str(o)
        return hashlib.sha256(json.dumps(self.G, default=d, sort_keys=True).encode()).hexdigest()[:16]


# =============================================================================
# DEMO sobre Psi
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

    u = UOG_last36(Psi, name="Psi")
    g = u.run()

    print("=" * 80)
    print("CAPAS 36-72 SOBRE PSI")
    print("=" * 80)
    for i, k in enumerate(sorted(g.keys()), 1):
        v = g[k]
        if isinstance(v, float):
            print(f"  [{i:>2}] {k:>22} = {v:+.10f}")
        else:
            print(f"  [{i:>2}] {k:>22} = {v}")

    print(f"\nTotal features: {len(g)}")
    print(f"HASH = {u.hash()}")

    with open("psi_last36.json", "w", encoding="utf-8") as f:
        json.dump({k: (v if not isinstance(v, (np.integer, np.floating)) else float(v))
                   for k, v in g.items()}, f, indent=2, ensure_ascii=False, default=str)
    print("Guardado: psi_last36.json")
