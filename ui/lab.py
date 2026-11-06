"""Generative AI Lab: a tiny PyTorch VAE and GAN trained live on 8x8 shape images."""
import time
import numpy as np
import streamlit as st

NAMES = ["Horizontal bar", "Vertical bar", "Diagonal", "Square"]


def make_data(n=800, seed=0):
    rng = np.random.default_rng(seed)
    X = np.zeros((n, 8, 8), np.float32)
    y = rng.integers(0, 4, n)
    for i, c in enumerate(y):
        if c == 0:
            X[i, rng.integers(1, 7), 1:7] = 1
        elif c == 1:
            X[i, 1:7, rng.integers(1, 7)] = 1
        elif c == 2:
            off = rng.integers(-1, 2)
            for k in range(8):
                if 0 <= k + off < 8:
                    X[i, k, k + off] = 1
        else:
            r, c0 = rng.integers(0, 5, 2)
            X[i, r:r + 3, c0:c0 + 3] = 1
    X = np.clip(X + rng.normal(0, 0.05, X.shape), 0, 1).astype(np.float32)
    return X.reshape(n, 64), y


def mosaic(imgs, cols, scale=6):
    n = len(imgs)
    rows = -(-n // cols)
    canvas = np.full((rows * 9, cols * 9), 0.35, np.float32)
    for i, im in enumerate(imgs):
        r, c = divmod(i, cols)
        canvas[r * 9:r * 9 + 8, c * 9:c * 9 + 8] = np.asarray(im).reshape(8, 8)
    return np.kron(canvas, np.ones((scale, scale), np.float32))


@st.cache_data(show_spinner=False)
def run_lab(epochs):
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    X, y = make_data()
    Xt = torch.tensor(X)

    class VAE(nn.Module):
        def __init__(s):
            super().__init__()
            s.e, s.mu, s.lv = nn.Linear(64, 48), nn.Linear(48, 2), nn.Linear(48, 2)
            s.d1, s.d2 = nn.Linear(2, 48), nn.Linear(48, 64)

        def encode(s, x):
            h = F.relu(s.e(x))
            return s.mu(h), s.lv(h)

        def decode(s, z):
            return torch.sigmoid(s.d2(F.relu(s.d1(z))))

        def forward(s, x):
            mu, lv = s.encode(x)
            return s.decode(mu + torch.randn_like(mu) * torch.exp(0.5 * lv)), mu, lv

    # ---- VAE ----
    torch.manual_seed(0)
    vae = VAE()
    opt = torch.optim.Adam(vae.parameters(), 3e-3)
    t0, last = time.time(), 0.0
    for _ in range(epochs):
        perm, tot = torch.randperm(len(Xt)), 0.0
        for i in range(0, len(Xt), 64):
            xb = Xt[perm[i:i + 64]]
            rec, mu, lv = vae(xb)
            loss = (F.binary_cross_entropy(rec, xb, reduction="sum")
                    - 0.5 * torch.sum(1 + lv - mu ** 2 - lv.exp())) / len(xb)
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item() * len(xb)
        last = tot / len(Xt)
    vae_time = time.time() - t0

    # ---- GAN (same number of steps) ----
    G = nn.Sequential(nn.Linear(8, 48), nn.ReLU(), nn.Linear(48, 64), nn.Sigmoid())
    D = nn.Sequential(nn.Linear(64, 48), nn.LeakyReLU(0.2), nn.Linear(48, 1))
    og = torch.optim.Adam(G.parameters(), 2e-3, betas=(0.5, 0.999))
    od = torch.optim.Adam(D.parameters(), 2e-3, betas=(0.5, 0.999))
    bce = F.binary_cross_entropy_with_logits
    ones, zeros = torch.ones(64, 1), torch.zeros(64, 1)
    t0 = time.time()
    for _ in range(epochs * 13):
        real = Xt[torch.randint(0, len(Xt), (64,))]
        fake = G(torch.randn(64, 8))
        d_loss = bce(D(real), ones) + bce(D(fake.detach()), zeros)
        od.zero_grad(); d_loss.backward(); od.step()
        g_loss = bce(D(fake), ones)
        og.zero_grad(); g_loss.backward(); og.step()
    gan_time = time.time() - t0

    with torch.no_grad():
        mu, _ = vae.encode(Xt)
        recon = vae.decode(mu[:8])
        axis = np.linspace(2.5, -2.5, 7)
        grid = torch.tensor([[a, b] for b in axis for a in np.linspace(-2.5, 2.5, 7)], dtype=torch.float32)
        grid_imgs = vae.decode(grid)
        vae_samples = vae.decode(torch.randn(16, 2))
        gan_samples = G(torch.randn(16, 8))
        near = lambda s: float((torch.cdist(s, Xt).min(1).values ** 2).mean() / 64)
        vae_nn, gan_nn = near(vae_samples), near(gan_samples)
    return {
        "latent": [(float(a), float(b), int(c)) for (a, b), c in zip(mu.numpy(), y)],
        "data": mosaic(X[:16], 8), "recon": mosaic(np.concatenate([X[:8], recon.numpy()]), 8),
        "grid": mosaic(grid_imgs.numpy(), 7, 5), "vae_samples": mosaic(vae_samples.numpy(), 8),
        "gan_samples": mosaic(gan_samples.numpy(), 8),
        "m": {"vae_loss": last, "vae_time": vae_time, "gan_d": float(d_loss), "gan_g": float(g_loss),
              "gan_time": gan_time, "vae_nn": vae_nn, "gan_nn": gan_nn},
    }
