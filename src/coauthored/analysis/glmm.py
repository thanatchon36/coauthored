"""Binomial GLMM for the H3 robustness check (PREREGISTRATION §8): random intercept and slope per repo.

``logit(p_ij) = x_ij β + u_i0 + u_i1 t_ij``, ``u_i ~ N(0, Σ)``, fitted by maximising the Laplace approximation
to the marginal likelihood (lme4 ``glmer`` default, ``nAGQ = 1``). R is not a dependency, so the
model is written out here: each repository's random-effect mode is found by Newton steps vectorised across
repositories (2 × 2 systems in closed form), the outer problem is solved with L-BFGS over β and the Cholesky
factor of Σ, and Wald intervals come from a central-difference Hessian of the outer objective.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import polars as pl
from scipy.special import expit

STRATA = ("S1", "S2", "S3")


@dataclass
class Fit:
    beta: np.ndarray  # intercept, t, S2, S2·t, S3, S3·t (t in scaled units)
    cov: np.ndarray  # Wald covariance of beta
    sigma: np.ndarray  # random-effect covariance (scaled units)
    scale: float  # months per scaled unit of t
    loglik: float
    converged: bool

    def slope(self, contrast: np.ndarray) -> tuple[float, float, float]:
        """Per-month slope for a contrast over beta: estimate and Wald 95% interval."""
        est = float(contrast @ self.beta) / self.scale
        se = float(np.sqrt(max(contrast @ self.cov @ contrast, 0.0))) / self.scale
        return est, est - 1.96 * se, est + 1.96 * se

    def slopes(self) -> dict[str, tuple[float, float, float]]:
        e = np.eye(6)
        return {
            "S1": self.slope(e[1]),
            "S2": self.slope(e[1] + e[3]),
            "S3": self.slope(e[1] + e[5]),
            "S1-S3": self.slope(-e[5]),
        }


class _Data:
    """Repository × month arrays, zero-padded with a mask."""

    def __init__(self, d: pl.DataFrame, month_index: dict[str, int]) -> None:
        repos = sorted(d["repo"].unique().to_list())
        rows = {r: g for (r,), g in d.group_by(["repo"])}
        m = max(g.height for g in rows.values())
        shape = (len(repos), m)
        self.t, self.y, self.n = np.zeros(shape), np.zeros(shape), np.zeros(shape)
        self.mask = np.zeros(shape, dtype=bool)
        self.s2, self.s3 = np.zeros(len(repos)), np.zeros(len(repos))
        raw = np.asarray(list(month_index.values()), dtype=float)
        self.centre, self.scale = float(raw.mean()), float(max(raw.std(), 1.0))
        for i, r in enumerate(repos):
            g = rows[r]
            k = g.height
            self.t[i, :k] = [(month_index[x] - self.centre) / self.scale for x in g["month"].to_list()]
            self.y[i, :k], self.n[i, :k] = g["n_attr"].to_numpy(), g["n"].to_numpy()
            self.mask[i, :k] = True
            stratum = g["stratum"][0]
            self.s2[i], self.s3[i] = stratum == "S2", stratum == "S3"
        self.u = np.zeros((len(repos), 2))  # warm start for the inner Newton steps

    def fixed(self, beta: np.ndarray) -> np.ndarray:
        s2, s3 = self.s2[:, None], self.s3[:, None]
        out: np.ndarray = (
            beta[0] + beta[1] * self.t + s2 * (beta[2] + beta[3] * self.t) + s3 * (beta[4] + beta[5] * self.t)
        )
        return out


def _sigma(theta: np.ndarray) -> np.ndarray:
    lower = np.array([[np.exp(theta[0]), 0.0], [theta[1], np.exp(theta[2])]])
    out: np.ndarray = lower @ lower.T
    return out


def _laplace(data: _Data, beta: np.ndarray, theta: np.ndarray, iters: int = 60) -> float:
    """Laplace-approximate marginal log-likelihood (binomial constants dropped)."""
    sig = _sigma(theta)
    prec = np.linalg.inv(sig)
    eta0 = data.fixed(beta)
    u = data.u.copy()
    for _ in range(iters):
        eta = eta0 + u[:, :1] + u[:, 1:] * data.t
        mu = expit(eta)
        r = np.where(data.mask, data.y - data.n * mu, 0.0)
        w = np.where(data.mask, data.n * mu * (1 - mu), 0.0)
        g = np.column_stack([r.sum(1), (r * data.t).sum(1)]) - u @ prec
        h00 = (w).sum(1) + prec[0, 0]
        h01 = (w * data.t).sum(1) + prec[0, 1]
        h11 = (w * data.t**2).sum(1) + prec[1, 1]
        det = h00 * h11 - h01**2
        step = np.column_stack([(h11 * g[:, 0] - h01 * g[:, 1]) / det, (h00 * g[:, 1] - h01 * g[:, 0]) / det])
        u = u + np.clip(step, -1.0, 1.0)  # damped: full Newton steps overshoot far from the mode
        if np.abs(step).max() < 1e-8:
            break
    if np.isfinite(u).all():
        data.u = u
    eta = eta0 + u[:, :1] + u[:, 1:] * data.t
    ll = np.where(data.mask, data.y * eta - data.n * np.logaddexp(0, eta), 0.0).sum(1)
    mu = expit(eta)
    w = np.where(data.mask, data.n * mu * (1 - mu), 0.0)
    h00, h01, h11 = (
        w.sum(1) + prec[0, 0],
        (w * data.t).sum(1) + prec[0, 1],
        (w * data.t**2).sum(1) + prec[1, 1],
    )
    quad = np.einsum("ij,jk,ik->i", u, prec, u)
    logdet_sig = np.linalg.slogdet(sig)[1]
    return float((ll - 0.5 * quad - 0.5 * logdet_sig - 0.5 * np.log(h00 * h11 - h01**2)).sum())


def _hessian(f: Callable[[np.ndarray], float], x: np.ndarray, h: float = 1e-3) -> np.ndarray:
    k = len(x)
    out = np.zeros((k, k))
    for i in range(k):
        for j in range(i, k):
            ei, ej = np.eye(k)[i] * h, np.eye(k)[j] * h
            out[i, j] = out[j, i] = (f(x + ei + ej) - f(x + ei - ej) - f(x - ei + ej) + f(x - ei - ej)) / (
                4 * h * h
            )
    return out


def fit(d: pl.DataFrame, month_index: dict[str, int]) -> Fit:
    """``d``: repo, stratum, month, n, n_attr (rows with n > 0); ``month_index``: month → integer index."""
    from scipy.optimize import minimize

    data = _Data(d.filter(pl.col("n") > 0), month_index)
    total = data.y[data.mask].sum() / data.n[data.mask].sum()
    x0 = np.r_[np.log(total / (1 - total)), np.zeros(5), 0.0, 0.0, -1.0]

    def nll(x: np.ndarray) -> float:
        return -_laplace(data, x[:6], x[6:])

    res = minimize(nll, x0, method="L-BFGS-B", options={"maxiter": 2000})
    nll(res.x)  # random effects at the optimum, not at the optimiser's last trial point
    mode = data.u.copy()

    def nll_at_mode(x: np.ndarray) -> float:
        data.u = mode.copy()  # every Hessian evaluation starts from the same random effects: path-independent
        return nll(x)

    hess = _hessian(nll_at_mode, res.x)
    try:
        cov = np.linalg.inv(hess)[:6, :6]
    except np.linalg.LinAlgError:
        cov = np.full((6, 6), np.nan)
    return Fit(res.x[:6], cov, _sigma(res.x[6:]), data.scale, -float(res.fun), bool(res.success))
