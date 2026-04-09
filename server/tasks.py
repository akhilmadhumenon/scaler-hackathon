"""
Instrument universes and task configurations for all four difficulty levels.
"""

from typing import Any

# ─── Task 1: Basic Screen (Easy) ─────────────────────────────────────────────
# 5 names, agent assigns overweight / neutral / underweight only.
# Reward: 0.20 per correct label. Max = 1.0

TASK_BASIC_SCREEN: dict[str, Any] = {
    "name": "basic_screen",
    "difficulty": "easy",
    "description": (
        "You are covering five liquid equities ahead of rebalance. For each name, "
        "issue a relative benchmark stance: 'overweight', 'neutral', or 'underweight'."
    ),
    "instructions": (
        "Stance definitions:\n"
        "  overweight   – Raise portfolio weight vs policy benchmark (conviction / upside skew)\n"
        "  neutral      – Keep near benchmark weight\n"
        "  underweight  – Reduce vs benchmark (risk, valuation, or deteriorating fundamentals)\n\n"
        "For each step respond with valid JSON ONLY:\n"
        '  {"instrument_id": "<id>", "decision": "<overweight|neutral|underweight>"}\n'
        "Process one instrument per step that is still pending."
    ),
    "max_steps": 5,
    "instruments": [
        {
            "id": "s1",
            "symbol": "CLOUD",
            "company": "Nimbus Cloud Systems Inc.",
            "sector": "Software",
            "headline": "FY guide cut 8%; net retention slipped below 110%",
            "narrative": (
                "Management cited elongated sales cycles and downsell among SMB accounts. "
                "Rule-of-40 now negative; cash burn widening while competitors bundle AI features "
                "at no incremental price. Street estimates still look 15% too high for FY2."
            ),
            "as_of": "2024-03-15T09:00:00Z",
        },
        {
            "id": "s2",
            "symbol": "CHIP",
            "company": "Lattice Semi Devices",
            "sector": "Semiconductors",
            "headline": "Q4 beat + raise; data-centre attach accelerates",
            "narrative": (
                "Revenue +22% YoY, gross margin +180 bps QoQ. CEO guided Q1 above consensus citing "
                "backlog coverage into Q3. Two hyperscalers named the firm as qualified vendor for "
                "next-gen accelerators. Net cash 1.2× revenue; buyback expanded."
            ),
            "as_of": "2024-03-15T09:15:00Z",
        },
        {
            "id": "s3",
            "symbol": "UTIL",
            "company": "Great Plains Electric Co.",
            "sector": "Utilities",
            "headline": "Rate case settled in-line; dividend growth 3% affirmed",
            "narrative": (
                "Regulators approved a 7-year capex plan with allowed ROE unchanged. "
                "No material surprises in weather-normalised load. Balance sheet metrics stable; "
                "valuation trades in line with regulated peers."
            ),
            "as_of": "2024-03-15T08:30:00Z",
        },
        {
            "id": "s4",
            "symbol": "PHRM",
            "company": "Helix Therapeutics",
            "sector": "Biotech",
            "headline": "FDA places Phase 3 trial on partial clinical hold",
            "narrative": (
                "Agency flagged hepatotoxicity signals in an overlapping patient cohort. "
                "Primary endpoint readout delayed at least 12 months; partner opt-out clause "
                "may trigger if hold exceeds 180 days. Cash runway ~8 quarters at current burn."
            ),
            "as_of": "2024-03-15T10:00:00Z",
        },
        {
            "id": "s5",
            "symbol": "RET",
            "company": "Urban Outfitters Collective",
            "sector": "Consumer Discretionary",
            "headline": "Same-store sales flat; promotional intensity elevated",
            "narrative": (
                "Traffic down low-single-digits but AUR held. Inventory days up modestly; "
                "no clearance risk flagged on call. Balance sheet conservative; dividend policy "
                "unchanged. Story is neither broken nor accelerating."
            ),
            "as_of": "2024-03-15T08:45:00Z",
        },
    ],
    "ground_truth": {
        "s1": {"decision": "underweight"},
        "s2": {"decision": "overweight"},
        "s3": {"decision": "neutral"},
        "s4": {"decision": "underweight"},
        "s5": {"decision": "neutral"},
    },
    "decision_reward": 0.20,
    "risk_tier_reward": 0.0,
    "thesis_reward": 0.0,
    "hedge_reward": 0.0,
    "thesis_required_for": [],
    "ordering_bonus": 0.0,
    "priority_ids": ["s2", "s4"],  # high-impact decisions first (conviction adds / risk cuts)
}


# ─── Task 2: Sector Rotation (Medium) ────────────────────────────────────────
# 10 instruments; stance + risk tier; thesis required for the cycle inflection name.

TASK_SECTOR_ROTATION: dict[str, Any] = {
    "name": "sector_rotation",
    "difficulty": "medium",
    "description": (
        "Rotate a 10-name sleeve across sectors. Label each with overweight/neutral/underweight "
        "and a risk tier (defensive/balanced/aggressive). Produce a concise thesis for the "
        "commodity cyclical where the cycle is inflecting (id='sr3')."
    ),
    "instructions": (
        "For every instrument provide decision and risk_tier.\n"
        "For id='sr3' (thermal services OEM tied to LNG capex) you MUST include a non-empty "
        "'thesis' explaining the cycle call.\n\n"
        "STRATEGY TIP: Decide high-impact cyclical and rate-sensitive names early for an ordering bonus.\n\n"
        "JSON ONLY per step:\n"
        '  {"instrument_id":"<id>","decision":"<overweight|neutral|underweight>",'
        ' "risk_tier":"<defensive|balanced|aggressive>",'
        ' "thesis":"<text or null>"}\n'
    ),
    "max_steps": 10,
    "instruments": [
        {
            "id": "sr1",
            "symbol": "BANK",
            "company": "Continental Trust Corp.",
            "sector": "Financials",
            "headline": "NIM outlook stable; credit costs normalising",
            "narrative": (
                "Net interest margin guided flat QoQ; loan growth low-mid single digits. "
                "CECL build modest; consumer delinquencies seasonally higher but within plan."
            ),
            "as_of": "2024-03-15T09:00:00Z",
        },
        {
            "id": "sr2",
            "symbol": "REIT",
            "company": "Metro Income Properties",
            "sector": "Real Estate",
            "headline": "Refinancing wall 18 months out; occupancy resilient",
            "narrative": (
                "Class-A office 92% leased; weighted avg maturity 3.2y. Debt covenants comfortable "
                "but refinancing spreads widened 40 bps vs last year."
            ),
            "as_of": "2024-03-15T08:30:00Z",
        },
        {
            "id": "sr3",
            "symbol": "TURB",
            "company": "Turbine Services International",
            "sector": "Industrials",
            "headline": "LNG train order book doubles; backlog visibility 36 months",
            "narrative": (
                "Book-to-bill >1.4× for two straight quarters. Management flagged FID acceleration "
                "on Qatar expansion trains and US Gulf brownfield debottlenecking. Margins inflecting "
                "as pricing power returns after three years of cost absorption."
            ),
            "as_of": "2024-03-15T07:45:00Z",
        },
        {
            "id": "sr4",
            "symbol": "TEL",
            "company": "Orbit Telecom",
            "sector": "Communication Services",
            "headline": "Wireless ARPU +2%; fibre build pacing plan",
            "narrative": (
                "Postpaid phone churn best-in-class. Capex intensity peaking; FCF inflection expected H2."
            ),
            "as_of": "2024-03-15T09:30:00Z",
        },
        {
            "id": "sr5",
            "symbol": "OIL",
            "company": "Prairie Shale Partners LP",
            "sector": "Energy",
            "headline": "Hedges roll off into backwardation",
            "narrative": (
                "70% of FY production hedged at $72/bbl; unhedged exposure rises materially next fiscal year. "
                "Breakevens competitive but balance sheet levered 2.1× through-cycle."
            ),
            "as_of": "2024-03-15T08:00:00Z",
        },
        {
            "id": "sr6",
            "symbol": "PKG",
            "company": "BoxCraft Packaging",
            "sector": "Materials",
            "headline": "Containerboard pricing soft; destocking tail end",
            "narrative": (
                "Volumes down 6% YoY; price gives back Q4 increases. Working capital release helped cash "
                "but outlook cautious on e-commerce packaging mix."
            ),
            "as_of": "2024-03-15T10:00:00Z",
        },
        {
            "id": "sr7",
            "symbol": "HLT",
            "company": "Summit Hotels Group",
            "sector": "Consumer Discretionary",
            "headline": "RevPAR +9% in gateway cities; group bookings recovering",
            "narrative": (
                "Urban luxury outperforming; asset sales programme 60% complete. Net leverage trending to 2.5×."
            ),
            "as_of": "2024-03-15T09:15:00Z",
        },
        {
            "id": "sr8",
            "symbol": "DEF",
            "company": "Sentinel Aero Systems",
            "sector": "Industrials",
            "headline": "Classified backlog growth; budget clarity through FY26",
            "narrative": (
                "Multi-year awards on missile-defence modernisation; sole-source on two programmes."
            ),
            "as_of": "2024-03-15T10:30:00Z",
        },
        {
            "id": "sr9",
            "symbol": "APP",
            "company": "ScrollFeed Inc.",
            "sector": "Technology",
            "headline": "DAU flat; ad pricing down high single digits",
            "narrative": (
                "Engagement minutes stable but monetisation weak. New AI features not yet revenue-bearing; "
                "competitive intensity from short-form rivals."
            ),
            "as_of": "2024-03-15T08:15:00Z",
        },
        {
            "id": "sr10",
            "symbol": "CHEM",
            "company": "VoltChem AG",
            "sector": "Materials",
            "headline": "European energy pass-through complete; spreads normalise",
            "narrative": (
                "Spreads vs Asia peers back to long-run median. Working capital a tailwind this quarter."
            ),
            "as_of": "2024-03-15T11:00:00Z",
        },
    ],
    "ground_truth": {
        "sr1": {"decision": "neutral", "risk_tier": "balanced"},
        "sr2": {"decision": "underweight", "risk_tier": "defensive"},
        "sr3": {"decision": "overweight", "risk_tier": "aggressive"},
        "sr4": {"decision": "overweight", "risk_tier": "balanced"},
        "sr5": {"decision": "underweight", "risk_tier": "defensive"},
        "sr6": {"decision": "underweight", "risk_tier": "defensive"},
        "sr7": {"decision": "overweight", "risk_tier": "balanced"},
        "sr8": {"decision": "overweight", "risk_tier": "balanced"},
        "sr9": {"decision": "underweight", "risk_tier": "balanced"},
        "sr10": {"decision": "neutral", "risk_tier": "balanced"},
    },
    # 10 × (0.015 + 0.015) = 0.30 decision+risk; + 0.60 thesis; + 0.10 ordering = 1.00
    "decision_reward": 0.015,
    "risk_tier_reward": 0.015,
    "thesis_reward": 0.60,
    "hedge_reward": 0.0,
    "thesis_required_for": ["sr3"],
    "thesis_keywords": {
        "sr3": {
            "keywords": [
                "lng", "capex", "cycle", "backlog", "margin", "pricing", "orders",
                "inflect", "inflection", "train", "book", "demand", "capacity",
            ],
            "required_matches": 3,
        },
    },
    "ordering_bonus": 0.10,
    "priority_ids": ["sr3", "sr5", "sr8", "sr9"],
}


# ─── Task 3: Risk Budget (Hard) ──────────────────────────────────────────────
# 15 instruments; decision + risk tier + theses for three critical names.

_DECISION_EACH = round(0.15 / 15, 6)
_RISK_EACH = round(0.25 / 15, 6)
_THESIS_EACH = 0.15

TASK_RISK_BUDGET: dict[str, Any] = {
    "name": "risk_budget",
    "difficulty": "hard",
    "description": (
        "Manage a 15-name book with benchmark-relative stances and explicit risk budgets per name. "
        "Draft theses for the liquidity event (rb4), the regulatory overhang (rb9), and the "
        "concentrated customer risk (rb12)."
    ),
    "instructions": (
        "Each step handles one pending instrument.\n"
        "Provide decision, risk_tier, and thesis (null except for rb4, rb9, rb12 where thesis is mandatory).\n\n"
        "STRATEGY TIP: Address tail-risk and liquidity-sensitive names early to capture ordering bonus.\n\n"
        "JSON ONLY:\n"
        '  {"instrument_id":"<id>","decision":"<overweight|neutral|underweight>",'
        ' "risk_tier":"<defensive|balanced|aggressive>",'
        ' "thesis":"<text or null>"}\n'
    ),
    "max_steps": 15,
    "instruments": [
        {
            "id": "rb1",
            "symbol": "INDEX",
            "company": "Global Core ETF Sleeve",
            "sector": "Multi-Asset",
            "headline": "Policy beta ~1.0; tracking error 35 bps",
            "narrative": "Plain-vanilla implementation; futures roll optimised; securities lending income +8 bps.",
            "as_of": "2024-03-15T08:00:00Z",
        },
        {
            "id": "rb2",
            "symbol": "FINT",
            "company": "PayStream Holdings",
            "sector": "Financials",
            "headline": "Take-rate stable; SMB TAM expanding",
            "narrative": "Volume +14% YoY; fraud losses contained. New enterprise wins offset churn in micro-merchants.",
            "as_of": "2024-03-15T09:00:00Z",
        },
        {
            "id": "rb3",
            "symbol": "AUTO",
            "company": "VoltDrive Motors",
            "sector": "Consumer Discretionary",
            "headline": "EV price cuts compress gross margin 300 bps",
            "narrative": (
                "Management prioritised share vs margin; warranty accruals rising on new platform. "
                "China joint-venture economics uncertain."
            ),
            "as_of": "2024-03-15T09:30:00Z",
        },
        {
            "id": "rb4",
            "symbol": "BOND",
            "company": "RiverCity HY Paper 2031",
            "sector": "Fixed Income",
            "headline": "Issuer announces consent solicitation + PIK toggle discussion",
            "narrative": (
                "Cash interest coverage slipped below 1.3×; covenants spring if liquidity < $120m. "
                "Ad-hoc group forming; secondary prints 62 cents with gaps on size."
            ),
            "as_of": "2024-03-15T07:30:00Z",
        },
        {
            "id": "rb5",
            "symbol": "AI",
            "company": "CogniStack Ltd.",
            "sector": "Software",
            "headline": "Inference GPU spend +40% QoQ; enterprise pipeline strong",
            "narrative": "NRR 128%; RPO doubled. Operating margin still negative but improving on scale.",
            "as_of": "2024-03-15T10:00:00Z",
        },
        {
            "id": "rb6",
            "symbol": "MINE",
            "company": "RedEarth Lithium",
            "sector": "Materials",
            "headline": "Spodumene contract repriced; China spot weak",
            "narrative": "Realised prices down 22% QoQ; unit costs sticky. Financing needed for Phase 2 expansion.",
            "as_of": "2024-03-15T08:45:00Z",
        },
        {
            "id": "rb7",
            "symbol": "MEDIA",
            "company": "NorthStar Broadcasting",
            "sector": "Communication Services",
            "headline": "Sports rights renewals 8% cost inflation",
            "narrative": "Affiliate fee growth offsets part of rights; leverage targeted <3.5× by FY25.",
            "as_of": "2024-03-15T10:15:00Z",
        },
        {
            "id": "rb8",
            "symbol": "INS",
            "company": "Harbor Indemnity Group",
            "sector": "Financials",
            "headline": "Cat losses within budget; reserve releases modest",
            "narrative": "Combined ratio 94; investment income tailwind from higher yields.",
            "as_of": "2024-03-15T11:00:00Z",
        },
        {
            "id": "rb9",
            "symbol": "DATA",
            "company": "CitizenGraph Analytics",
            "sector": "Technology",
            "headline": "EU draft rule would ban certain cross-border inference patterns",
            "narrative": (
                "Proposal could force regional model shards; engineering estimate 18-month remediation. "
                "Enterprise contracts have weak change-of-law clauses."
            ),
            "as_of": "2024-03-15T07:00:00Z",
        },
        {
            "id": "rb10",
            "symbol": "SHOP",
            "company": "QuickCart Retail",
            "sector": "Consumer Staples",
            "headline": "Private label mix +200 bps; shrink improving",
            "narrative": "Traffic soft but basket up; online penetration plateaued near 18%.",
            "as_of": "2024-03-15T09:45:00Z",
        },
        {
            "id": "rb11",
            "symbol": "AIR",
            "company": "JetStream Airways",
            "sector": "Industrials",
            "headline": "RASM +6%; fuel hedge 60% through summer",
            "narrative": "International long-haul lagging domestic; fleet orderbook flexible post-2026.",
            "as_of": "2024-03-15T10:30:00Z",
        },
        {
            "id": "rb12",
            "symbol": "RET2",
            "company": "MonoBrand Outfitters",
            "sector": "Consumer Discretionary",
            "headline": "Top customer represents 34% of revenue; contract renewal in 9 months",
            "narrative": (
                "Customer consolidating vendors; RFP live. If lost, EBITDA impact ~22%; no ready replacement pipeline."
            ),
            "as_of": "2024-03-15T08:15:00Z",
        },
        {
            "id": "rb13",
            "symbol": "HOSP",
            "company": "CarePeak Hospitals",
            "sector": "Health Care",
            "headline": "Payer mix shift mildly negative",
            "narrative": "Same-facility admissions +2%; commercial mix down 80 bps YoY.",
            "as_of": "2024-03-15T11:15:00Z",
        },
        {
            "id": "rb14",
            "symbol": "SOLR",
            "company": "HelioPanel Technologies",
            "sector": "Industrials",
            "headline": "IRA credits support margin; polysilicon input costs volatile",
            "narrative": "Backlog covers 14 months; execution risk on new factory ramp.",
            "as_of": "2024-03-15T09:20:00Z",
        },
        {
            "id": "rb15",
            "symbol": "GOLD",
            "company": "Royal Reef Mining",
            "sector": "Materials",
            "headline": "AISC up 7% on diesel; realised gold +4%",
            "narrative": "Free cash flow positive; net debt zero; dividend policy under review.",
            "as_of": "2024-03-15T12:00:00Z",
        },
    ],
    "ground_truth": {
        "rb1": {"decision": "neutral", "risk_tier": "balanced"},
        "rb2": {"decision": "overweight", "risk_tier": "balanced"},
        "rb3": {"decision": "underweight", "risk_tier": "defensive"},
        "rb4": {"decision": "underweight", "risk_tier": "defensive"},
        "rb5": {"decision": "overweight", "risk_tier": "aggressive"},
        "rb6": {"decision": "underweight", "risk_tier": "defensive"},
        "rb7": {"decision": "neutral", "risk_tier": "balanced"},
        "rb8": {"decision": "overweight", "risk_tier": "balanced"},
        "rb9": {"decision": "underweight", "risk_tier": "defensive"},
        "rb10": {"decision": "neutral", "risk_tier": "balanced"},
        "rb11": {"decision": "overweight", "risk_tier": "balanced"},
        "rb12": {"decision": "underweight", "risk_tier": "defensive"},
        "rb13": {"decision": "neutral", "risk_tier": "balanced"},
        "rb14": {"decision": "overweight", "risk_tier": "balanced"},
        "rb15": {"decision": "neutral", "risk_tier": "defensive"},
    },
    "decision_reward": _DECISION_EACH,
    "risk_tier_reward": _RISK_EACH,
    "thesis_reward": _THESIS_EACH,
    "hedge_reward": 0.0,
    "thesis_required_for": ["rb4", "rb9", "rb12"],
    "thesis_keywords": {
        "rb4": {
            "keywords": [
                "liquidity", "covenant", "default", "refinance", "consent", "coverage",
                "cash", "distressed", "credit", "runway", "pik", "senior", "yield",
            ],
            "required_matches": 2,
        },
        "rb9": {
            "keywords": [
                "regulatory", "eu", "compliance", "data", "risk", "remediation",
                "law", "cross-border", "engineering", "contract", "exposure",
            ],
            "required_matches": 2,
        },
        "rb12": {
            "keywords": [
                "concentration", "customer", "renewal", "rfp", "revenue", "risk",
                "vendor", "ebitda", "replace", "diversify", "contract", "churn",
            ],
            "required_matches": 2,
        },
    },
    "ordering_bonus": 0.15,
    "priority_ids": ["rb4", "rb9", "rb12", "rb3", "rb6"],
}


# ─── Task 4: Macro Stress (Expert) ───────────────────────────────────────────
# 12 instruments; stance + risk tier + hedge flag + thesis for systemic tail name.

TASK_MACRO_STRESS: dict[str, Any] = {
    "name": "macro_stress",
    "difficulty": "expert",
    "description": (
        "Stress regime: rates volatile, credit dispersion wide. For each name choose benchmark stance, "
        "risk tier, whether a hedge/overlay is warranted (hedge_recommended), and produce a thesis for "
        "the cross-asset liquidity hinge (ms7)."
    ),
    "instructions": (
        "Fields per step:\n"
        "  decision            – overweight | neutral | underweight\n"
        "  risk_tier           – defensive | balanced | aggressive\n"
        "  hedge_recommended   – true if options, futures overlay, or CDS hedge is justified\n"
        "  thesis              – required for ms7; null otherwise\n\n"
        "HEDGE HEURISTICS:\n"
        "  – High beta + stretched liquidity + event risk → often true\n"
        "  – Investment-grade balance sheet + low cash-flow volatility → usually false\n"
        "  – Illiquid credit with cliff-style maturities → often true\n\n"
        "STRATEGY TIP: Address liquidity/event clusters early.\n\n"
        "JSON ONLY:\n"
        '  {"instrument_id":"<id>","decision":"<...>","risk_tier":"<...>",'
        ' "hedge_recommended":<true|false>,"thesis":"<text or null>"}\n'
    ),
    "max_steps": 12,
    "instruments": [
        {
            "id": "ms1",
            "symbol": "MMKT",
            "company": "Treasury MMF Sleeve",
            "sector": "Cash",
            "headline": "WAL 45 days; stable NAV",
            "narrative": "Government-only holdings; no credit spread exposure; minimal term risk.",
            "as_of": "2024-03-15T06:00:00Z",
        },
        {
            "id": "ms2",
            "symbol": "JNK",
            "company": "HY Beta ETF",
            "sector": "Fixed Income",
            "headline": "OAS +120 bps from tights; flows negative 3 weeks",
            "narrative": "Duration ~3.8y; high sensitivity to growth scares and funding stress.",
            "as_of": "2024-03-15T07:00:00Z",
        },
        {
            "id": "ms3",
            "symbol": "MEGA",
            "company": "OmniConsumer Brands",
            "sector": "Consumer Staples",
            "headline": "Volume/mix slightly negative; pricing +4%",
            "narrative": "Emerging markets soft; developed resilient. Net debt/EBITDA 2.1×.",
            "as_of": "2024-03-15T08:00:00Z",
        },
        {
            "id": "ms4",
            "symbol": "LEVC",
            "company": "Levered CLO Equity Tranche",
            "sector": "Structured Credit",
            "headline": "OC cushions thinning; CCC bucket 8.4%",
            "narrative": (
                "Two loans on watchlist; manager testing auction rules. Equity cash-on-cash yield attractive "
                "but tail risk non-linear if defaults cluster."
            ),
            "as_of": "2024-03-15T07:15:00Z",
        },
        {
            "id": "ms5",
            "symbol": "RATE",
            "company": "Duration Overlay Fund",
            "sector": "Rates",
            "headline": "Key rate DV01 concentrated 5y–7y",
            "narrative": "Explicitly used to hedge liability-driven portfolios; negative carry 45 bps.",
            "as_of": "2024-03-15T08:30:00Z",
        },
        {
            "id": "ms6",
            "symbol": "BANK2",
            "company": "Frontier Regional Bancorp",
            "sector": "Financials",
            "headline": "CRE office exposure 18% of loans; ACL build +$40m",
            "narrative": "Core capital still adequate; marks on NYC/SF loans conservative vs marks.",
            "as_of": "2024-03-15T09:00:00Z",
        },
        {
            "id": "ms7",
            "symbol": "XASW",
            "company": "Cross-Asset Swap Hub Note",
            "sector": "Multi-Asset",
            "headline": "Bilateral CSA tightening; VM calls on equity leg",
            "narrative": (
                "Prime broker raised margin 35% on equity index leg; funding desk cites balance-sheet scarcity. "
                "Note references dynamic deleveraging triggers tied to VIX and IG CDX. Liquidity hinge for pod books."
            ),
            "as_of": "2024-03-15T06:30:00Z",
        },
        {
            "id": "ms8",
            "symbol": "EM",
            "company": "LatAm Local Debt Fund",
            "sector": "Emerging Markets",
            "headline": "FX hedged share class; carry 8.2%",
            "narrative": "Election calendar noisy; central banks mostly orthodox; positioning crowded long.",
            "as_of": "2024-03-15T09:30:00Z",
        },
        {
            "id": "ms9",
            "symbol": "PHAR",
            "company": "GlobeForm Pharma",
            "sector": "Health Care",
            "headline": "Patent cliff 18 months out; pipeline optionality underappreciated",
            "narrative": "Two Phase 3 readouts in next 9 months; balance sheet supports BD.",
            "as_of": "2024-03-15T10:00:00Z",
        },
        {
            "id": "ms10",
            "symbol": "VOL",
            "company": "Variance Risk Premium Harvest",
            "sector": "Derivatives",
            "headline": "Short vol exposure capped daily",
            "narrative": "Strategy explicitly sells index variance within loss limits; convexity bleed in calm tapes.",
            "as_of": "2024-03-15T10:30:00Z",
        },
        {
            "id": "ms11",
            "symbol": "REIT2",
            "company": "Coastal Mall REIT",
            "sector": "Real Estate",
            "headline": "CMBS maturity 14 months; extension unlikely without equity",
            "narrative": "Anchor tenant in bankruptcy; co-tenancy clauses triggered on two assets.",
            "as_of": "2024-03-15T07:45:00Z",
        },
        {
            "id": "ms12",
            "symbol": "SEMIS",
            "company": "EdgeWafer Foundry",
            "sector": "Semiconductors",
            "headline": "Leading-edge utilisation 94%; capex guided +11%",
            "narrative": "Long-term supply agreements with hyperscalers; geopolitical export controls a tail risk.",
            "as_of": "2024-03-15T11:00:00Z",
        },
    ],
    "ground_truth": {
        "ms1": {"decision": "neutral", "risk_tier": "defensive", "hedge_recommended": False},
        "ms2": {"decision": "underweight", "risk_tier": "defensive", "hedge_recommended": True},
        "ms3": {"decision": "neutral", "risk_tier": "balanced", "hedge_recommended": False},
        "ms4": {"decision": "underweight", "risk_tier": "aggressive", "hedge_recommended": True},
        "ms5": {"decision": "overweight", "risk_tier": "defensive", "hedge_recommended": False},
        "ms6": {"decision": "underweight", "risk_tier": "defensive", "hedge_recommended": True},
        "ms7": {"decision": "underweight", "risk_tier": "defensive", "hedge_recommended": True},
        "ms8": {"decision": "neutral", "risk_tier": "balanced", "hedge_recommended": True},
        "ms9": {"decision": "overweight", "risk_tier": "balanced", "hedge_recommended": False},
        "ms10": {"decision": "underweight", "risk_tier": "aggressive", "hedge_recommended": True},
        "ms11": {"decision": "underweight", "risk_tier": "defensive", "hedge_recommended": True},
        "ms12": {"decision": "overweight", "risk_tier": "balanced", "hedge_recommended": True},
    },
    "decision_reward": round(0.15 / 12, 6),
    "risk_tier_reward": round(0.25 / 12, 6),
    "hedge_reward": round(0.30 / 12, 6),
    "thesis_reward": 0.15,
    "thesis_required_for": ["ms7"],
    "thesis_keywords": {
        "ms7": {
            "keywords": [
                "liquidity", "margin", "funding", "volatility", "delever", "hedge",
                "swap", "prime", "broker", "vm", "collateral", "csa", "risk",
            ],
            "required_matches": 3,
        },
    },
    "ordering_bonus": 0.15,
    "priority_ids": ["ms7", "ms4", "ms11", "ms2", "ms6"],
}


ALL_TASKS = {
    "basic_screen": TASK_BASIC_SCREEN,
    "sector_rotation": TASK_SECTOR_ROTATION,
    "risk_budget": TASK_RISK_BUDGET,
    "macro_stress": TASK_MACRO_STRESS,
}
