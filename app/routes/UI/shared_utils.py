"""Shared utility functions for UI modules."""


def kmeans_1d(values, k, iters=20):
    """K-means clustering in 1D."""
    if not values or k <= 0:
        return []
    # initialize centers as quantiles
    vals = sorted(values)
    centers = []
    n = len(vals)
    for i in range(k):
        idx = int((i + 0.5) * n / k)
        centers.append(vals[min(idx, n - 1)])

    for _ in range(iters):
        groups = {i: [] for i in range(k)}
        for v in vals:
            best = min(range(k), key=lambda c: abs(v - centers[c]))
            groups[best].append(v)
        changed = False
        for i in range(k):
            if groups[i]:
                newc = sum(groups[i]) / len(groups[i])
                if abs(newc - centers[i]) > 1e-6:
                    changed = True
                centers[i] = newc
        if not changed:
            break
    return centers


def group_rows(words, y_thresh=8.0):
    """Group words into rows by y-center proximity."""
    rows = []
    for w in sorted(words, key=lambda x: (x["y0"] + x["y1"]) / 2):
        ymid = (w["y0"] + w["y1"]) / 2
        placed = False
        for r in rows:
            if abs(r["ymid"] - ymid) <= y_thresh:
                r["words"].append(w)
                # update average ymid
                r["ymid"] = sum(( (ww["y0"]+ww["y1"]) / 2 for ww in r["words"] )) / len(r["words"])
                placed = True
                break
        if not placed:
            rows.append({"ymid": ymid, "words": [w]})
    return rows
