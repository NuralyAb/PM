"""Clinic price benchmark (Change Request CR-01).

For every normalized service a clinic offers, compare its price with the same
service in other clinics of the same city: min / median / max, the clinic's rank
(1 = cheapest) and its deviation from the city median. Used by clinic clients to
see where they are over- or under-priced.
"""
from __future__ import annotations

import csv
import io
import uuid
from statistics import median

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Clinic, ServiceOffer
from app.schemas import BenchmarkItem, BenchmarkResponse, BenchmarkSummary
from app.services.queries import _stale_cutoff

AT_MEDIAN_TOLERANCE_PCT = 0.5  # within ±0.5 % of the median counts as "at median"


def position(price: float, market: list[float]) -> dict:
    """Place one clinic price within the market prices of the same service and city.

    `market` contains one price per clinic (including this clinic's own price).
    Pure function — no DB — so it is unit-tested directly.
    """
    if not market:
        raise ValueError("market must contain at least the clinic's own price")
    lo, hi, med = min(market), max(market), median(market)
    rank = 1 + sum(1 for p in market if p < price)  # ties share the better rank
    diff_pct = round((price - med) / med * 100, 1) if med else 0.0
    n = len(market)
    if n == 1:
        label = "no_competitors"
    elif price == lo:
        label = "cheapest"
    elif price == hi:
        label = "most_expensive"
    elif abs(diff_pct) <= AT_MEDIAN_TOLERANCE_PCT:
        label = "at_median"
    elif diff_pct < 0:
        label = "below_median"
    else:
        label = "above_median"
    return {
        "clinics_compared": n, "city_min": lo, "city_median": round(float(med), 2), "city_max": hi,
        "rank": rank, "diff_vs_median_pct": diff_pct, "position": label,
    }


def summarize(items: list[BenchmarkItem]) -> BenchmarkSummary:
    compared = [i for i in items if i.clinics_compared > 1]
    return BenchmarkSummary(
        services_total=len(items),
        services_compared=len(compared),
        cheapest_count=sum(1 for i in compared if i.position == "cheapest"),
        below_median_count=sum(1 for i in compared if i.diff_vs_median_pct < -AT_MEDIAN_TOLERANCE_PCT),
        above_median_count=sum(1 for i in compared if i.diff_vs_median_pct > AT_MEDIAN_TOLERANCE_PCT),
        most_expensive_count=sum(1 for i in compared if i.position == "most_expensive"),
        avg_diff_vs_median_pct=(
            round(sum(i.diff_vs_median_pct for i in compared) / len(compared), 1) if compared else 0.0
        ),
    )


async def clinic_benchmark(db: AsyncSession, clinic_id: uuid.UUID) -> BenchmarkResponse | None:
    clinic = await db.get(Clinic, clinic_id)
    if clinic is None:
        return None
    cutoff = _stale_cutoff()

    def _cheapest_per(rows, key):
        best: dict = {}
        for o in rows:
            k = key(o)
            if k not in best or float(o.price_kzt) < float(best[k].price_kzt):
                best[k] = o
        return best

    own_rows = (
        await db.execute(
            select(ServiceOffer)
            .options(selectinload(ServiceOffer.service))
            .where(
                ServiceOffer.clinic_id == clinic_id,
                ServiceOffer.service_id.isnot(None),
                ServiceOffer.is_active.is_(True),
                ServiceOffer.parsed_at >= cutoff,
            )
        )
    ).scalars().all()
    own = _cheapest_per(own_rows, lambda o: o.service_id)  # one price per service
    if not own:
        return BenchmarkResponse(clinic_id=str(clinic.id), clinic_name=clinic.name, city=clinic.city,
                                 items=[], summary=summarize([]))

    market_rows = (
        await db.execute(
            select(ServiceOffer)
            .join(Clinic, ServiceOffer.clinic_id == Clinic.id)
            .where(
                Clinic.city == clinic.city,
                ServiceOffer.service_id.in_(list(own.keys())),
                ServiceOffer.is_active.is_(True),
                ServiceOffer.parsed_at >= cutoff,
            )
        )
    ).scalars().all()
    # one (cheapest) price per clinic per service, so a clinic with duplicates counts once
    per_clinic = _cheapest_per(market_rows, lambda o: (o.service_id, o.clinic_id))
    market: dict = {}
    for (sid, _cid), o in per_clinic.items():
        market.setdefault(sid, []).append(float(o.price_kzt))

    items = []
    for sid, o in own.items():
        price = float(o.price_kzt)
        pos = position(price, market.get(sid, [price]))
        items.append(BenchmarkItem(
            service_id=str(sid), service_name_norm=o.service.name_norm if o.service else o.service_name_raw,
            category=o.service.category if o.service else "laboratory", price_kzt=price, **pos,
        ))
    # most actionable first: the most over-priced services relative to the city median
    items.sort(key=lambda i: (i.clinics_compared == 1, -i.diff_vs_median_pct))
    return BenchmarkResponse(clinic_id=str(clinic.id), clinic_name=clinic.name, city=clinic.city,
                             items=items, summary=summarize(items))


def to_csv(report: BenchmarkResponse) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["service", "category", "clinic_price_kzt", "city_min_kzt", "city_median_kzt", "city_max_kzt",
                "rank", "clinics_compared", "diff_vs_median_pct", "position"])
    for i in report.items:
        w.writerow([i.service_name_norm, i.category, i.price_kzt, i.city_min, i.city_median, i.city_max,
                    i.rank, i.clinics_compared, i.diff_vs_median_pct, i.position])
    return buf.getvalue()
