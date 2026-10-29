#!/usr/bin/env python3
"""Membuat 3 gambar SVG untuk README profil: stats.svg, langs.svg, activity.svg.

Data diambil dari GitHub GraphQL API. Hanya memakai library bawaan Python.
Env: GH_TOKEN (token), GH_USER (username). Jalankan dengan --mock untuk uji tampilan tanpa jaringan.
"""
import json, os, sys, math, random, urllib.request, datetime as dt
from html import escape

OUT = os.environ.get("OUT_DIR", "dist")
USER = os.environ.get("GH_USER", "sulthanrizal")
TOKEN = os.environ.get("GH_TOKEN", "")
FONT = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"

QUERY = """
query($login:String!){
  user(login:$login){
    name login followers{totalCount}
    contributionsCollection{
      totalCommitContributions totalIssueContributions
      totalPullRequestContributions totalPullRequestReviewContributions
      restrictedContributionsCount
      contributionCalendar{ totalContributions weeks{ firstDay contributionDays{ date contributionCount } } }
    }
    repositories(first:100, ownerAffiliations:OWNER, isFork:false, orderBy:{field:PUSHED_AT, direction:DESC}){
      totalCount
      nodes{ stargazerCount languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } }
    }
  }
}"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    if body.get("errors") or not body.get("data", {}).get("user"):
        raise SystemExit("GraphQL error: " + json.dumps(body.get("errors") or body)[:500])
    return body["data"]["user"]


def mock():
    random.seed(3)
    start = dt.date(2025, 11, 2)
    weeks = []
    for w in range(52):
        days = []
        for d in range(7):
            date = start + dt.timedelta(days=w * 7 + d)
            if date > dt.date(2026, 10, 30):
                continue
            busy = 1.0 if (w < 17 or w > 46) else 0.45
            c = int(max(0, random.gauss(4, 5)) * busy) if random.random() < 0.7 * busy + 0.1 else 0
            days.append({"date": date.isoformat(), "contributionCount": c})
        if days:
            weeks.append({"firstDay": days[0]["date"], "contributionDays": days})
    total = sum(d["contributionCount"] for w in weeks for d in w["contributionDays"])
    langs = [("TypeScript", "#3178c6", 520), ("JavaScript", "#f1e05a", 410), ("CSS", "#563d7c", 230),
             ("SCSS", "#c6538c", 120), ("HTML", "#e34c26", 90), ("Dart", "#00B4AB", 40), ("Shell", "#89e051", 20)]
    return {"name": "Sulthan Rizal Halfa 'Ilmi", "login": USER, "followers": {"totalCount": 14},
            "contributionsCollection": {"totalCommitContributions": 980, "totalIssueContributions": 12,
                                        "totalPullRequestContributions": 61, "totalPullRequestReviewContributions": 9,
                                        "restrictedContributionsCount": 0,
                                        "contributionCalendar": {"totalContributions": total, "weeks": weeks}},
            "repositories": {"totalCount": 31, "nodes": [{"stargazerCount": 7, "languages": {"edges": [
                {"size": s, "node": {"name": n, "color": c}} for n, c, s in langs]}}]}}


# ---------- komponen umum ----------
def defs(uid):
    return f'''<defs>
<linearGradient id="bd{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset=".5" stop-color="#6366f1"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
<linearGradient id="tt{uid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
<linearGradient id="bg{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#05050c"/><stop offset="1" stop-color="#0a0a1f"/></linearGradient>
</defs>'''


def card(w, h, uid, body, title, right=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
{defs(uid)}
<style>
text{{font-family:{FONT}}}
.t{{font-size:19px;font-weight:700;fill:url(#tt{uid})}}
.s{{font-size:12px;fill:#64748b}}
.l{{font-size:14px;fill:#94a3b8}}
.v{{font-size:15px;font-weight:700;fill:#e2e8f0}}
.fi{{opacity:0;animation:fi .6s ease-out forwards}}
@keyframes fi{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
</style>
<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="14" fill="url(#bg{uid})" stroke="url(#bd{uid})" stroke-opacity=".55" stroke-width="1.5"/>
<text x="28" y="40" class="t">{escape(title)}</text>
{f'<text x="{w-28}" y="39" class="s" text-anchor="end">{escape(right)}</text>' if right else ''}
{body}
</svg>'''


def fmt(n):
    return f"{n:,}"


# ---------- 1. stats ----------
def make_stats(u):
    cc = u["contributionsCollection"]
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    rows = [
        ("#22d3ee", "Contributions", cc["contributionCalendar"]["totalContributions"]),
        ("#818cf8", "Commits", cc["totalCommitContributions"] + cc["restrictedContributionsCount"]),
        ("#c084fc", "Pull Requests", cc["totalPullRequestContributions"]),
        ("#f472b6", "Code Reviews", cc["totalPullRequestReviewContributions"]),
        ("#34d399", "Issues", cc["totalIssueContributions"]),
        ("#fbbf24", "Stars Earned", stars),
        ("#60a5fa", "Repositories", u["repositories"]["totalCount"]),
        ("#fb923c", "Followers", u["followers"]["totalCount"]),
    ]
    b = []
    for i, (col, label, val) in enumerate(rows):
        cx = 28 if i < 4 else 262
        vx = 232 if i < 4 else 467
        y = 84 + (i % 4) * 36
        d = 0.15 + i * 0.09
        b.append(f'<g class="fi" style="animation-delay:{d:.2f}s"><circle cx="{cx+5}" cy="{y-5}" r="4.5" fill="{col}"/>'
                 f'<text x="{cx+18}" y="{y}" class="l">{label}</text><text x="{vx}" y="{y}" class="v" text-anchor="end">{fmt(val)}</text></g>')
    return card(495, 205, "s", "\n".join(b), "GitHub Stats", "last 12 months")


# ---------- 2. languages ----------
def make_langs(u):
    agg = {}
    for r in u["repositories"]["nodes"]:
        for e in (r["languages"]["edges"] or []):
            n = e["node"]["name"]
            a = agg.setdefault(n, [0, e["node"]["color"] or "#818cf8"])
            a[0] += e["size"]
    total = sum(v[0] for v in agg.values()) or 1
    top = sorted(agg.items(), key=lambda kv: -kv[1][0])[:6]
    b = []
    for i, (name, (size, col)) in enumerate(top):
        y = 80 + i * 20
        pct = size / total * 100
        bw = max(4, 245 * pct / 100 / (top[0][1][0] / total))  # bahasa teratas = bar penuh
        d = 0.15 + i * 0.1
        b.append(f'<g class="fi" style="animation-delay:{d:.2f}s"><text x="28" y="{y+4}" class="l">{escape(name)}</text>'
                 f'<rect x="130" y="{y-6}" width="245" height="10" rx="5" fill="#ffffff" fill-opacity=".06"/>'
                 f'<rect x="130" y="{y-6}" width="0" height="10" rx="5" fill="{escape(col)}"><animate attributeName="width" from="0" to="{bw:.1f}" dur="1s" begin="{d+0.1:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/></rect>'
                 f'<text x="467" y="{y+4}" class="v" text-anchor="end" style="font-size:13px">{pct:.1f}%</text></g>')
    return card(495, 205, "l", "\n".join(b), "Top Languages", "by code size")


# ---------- 3. activity ----------
def smooth(pts, lo, hi):
    if len(pts) < 3:
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(hi, max(lo, p1[1] + (p2[1] - p0[1]) / 6)))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(hi, max(lo, p2[1] - (p3[1] - p1[1]) / 6)))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def make_activity(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = [(w["firstDay"], sum(d["contributionCount"] for d in w["contributionDays"])) for w in cal["weeks"]]
    W, H = 1000, 290
    x0, x1, yt, yb = 56, 968, 92, 232
    vmax = max(v for _, v in weeks) or 1
    step = max(5, int(math.ceil(vmax / 4 / 5.0)) * 5)
    ymax = step * 4
    X = lambda i: x0 + (x1 - x0) * i / (len(weeks) - 1)
    Y = lambda v: yb - (yb - yt) * v / ymax
    pts = [(X(i), Y(v)) for i, (_, v) in enumerate(weeks)]
    line = smooth(pts, yt, yb)
    area = line + f" L{x1},{yb} L{x0},{yb} Z"
    g = []
    for k in range(5):
        y = yt + (yb - yt) * k / 4
        g.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#ffffff" stroke-opacity=".07" stroke-dasharray="3 5"/>'
                 f'<text x="{x0-12}" y="{y+4:.1f}" class="s" text-anchor="end">{ymax - step*k}</text>')
    seen = set()
    for i, (d0, _) in enumerate(weeks):
        m = d0[:7]
        if m not in seen and i < len(weeks) - 2:
            seen.add(m)
            mon = dt.date.fromisoformat(d0).strftime("%b")
            g.append(f'<text x="{X(i):.1f}" y="{yb+24}" class="s" text-anchor="middle">{mon}</text>')
    pk = max(range(len(weeks)), key=lambda i: weeks[i][1])
    px, py = pts[pk]
    tx = min(max(px, x0 + 50), x1 - 50)
    body = f'''<defs>
<linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#22d3ee" stop-opacity=".45"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></linearGradient>
<linearGradient id="ln" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset=".55" stop-color="#818cf8"/><stop offset="1" stop-color="#c084fc"/></linearGradient>
<filter id="gl" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="4"/></filter>
</defs>
{''.join(g)}
<path d="{area}" fill="url(#ar)" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="1.2s" begin="1.2s" fill="freeze"/></path>
<path d="{line}" fill="none" stroke="#22d3ee" stroke-width="5" opacity=".35" filter="url(#gl)" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"><animate attributeName="stroke-dashoffset" from="1" to="0" dur="2.2s" fill="freeze"/></path>
<path d="{line}" fill="none" stroke="url(#ln)" stroke-width="2.5" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"><animate attributeName="stroke-dashoffset" from="1" to="0" dur="2.2s" fill="freeze"/></path>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur=".5s" begin="2.2s" fill="freeze"/>
<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#0a0a1f" stroke="#22d3ee" stroke-width="2"/>
<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="none" stroke="#22d3ee"><animate attributeName="r" values="5;16" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="2s" repeatCount="indefinite"/></circle>
<text x="{tx:.1f}" y="{max(py-16, 74):.1f}" class="s" text-anchor="middle" style="fill:#e2e8f0">peak · {weeks[pk][1]} / week</text></g>'''
    return card(W, H, "a", body, "Contribution Activity", f"{fmt(cal['totalContributions'])} contributions in the last year")


def main():
    u = mock() if "--mock" in sys.argv else fetch()
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("stats.svg", make_stats), ("langs.svg", make_langs), ("activity.svg", make_activity)):
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(fn(u))
        print("wrote", os.path.join(OUT, name))


if __name__ == "__main__":
    main()
