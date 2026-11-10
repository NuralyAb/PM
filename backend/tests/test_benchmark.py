"""Unit tests for the clinic price benchmark (CR-01) — pure functions, no DB."""
from app.schemas import BenchmarkItem, BenchmarkResponse
from app.services.benchmark import position, summarize, to_csv


def _item(diff, pos, n=3):
    return BenchmarkItem(service_id="s", service_name_norm="Глюкоза крови", category="laboratory",
                         price_kzt=100, clinics_compared=n, city_min=90, city_median=100, city_max=120,
                         rank=1, diff_vs_median_pct=diff, position=pos)


def test_cheapest_clinic_ranks_first():
    p = position(480, [480, 930, 650])
    assert p["rank"] == 1 and p["position"] == "cheapest"
    assert p["city_min"] == 480 and p["city_max"] == 930 and p["city_median"] == 650


def test_most_expensive_clinic():
    p = position(930, [480, 930, 650])
    assert p["rank"] == 3 and p["position"] == "most_expensive"
    assert p["diff_vs_median_pct"] == 43.1  # (930-650)/650


def test_below_and_above_median():
    assert position(600, [500, 600, 700, 800])["position"] == "below_median"  # median 650
    assert position(700, [500, 600, 700, 800])["position"] == "above_median"


def test_at_median_tolerance():
    p = position(1001, [900, 1000, 1001, 1200])  # median 1000.5 → +0.05 %
    assert p["position"] == "at_median"


def test_single_clinic_has_no_competitors():
    p = position(1500, [1500])
    assert p["position"] == "no_competitors" and p["clinics_compared"] == 1 and p["diff_vs_median_pct"] == 0.0


def test_ties_share_the_better_rank():
    assert position(500, [500, 500, 900])["rank"] == 1


def test_empty_market_is_rejected():
    try:
        position(100, [])
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_summary_counts_only_compared_services():
    items = [_item(-10, "cheapest"), _item(20, "most_expensive"), _item(0, "no_competitors", n=1)]
    s = summarize(items)
    assert s.services_total == 3 and s.services_compared == 2
    assert s.cheapest_count == 1 and s.most_expensive_count == 1
    assert s.below_median_count == 1 and s.above_median_count == 1
    assert s.avg_diff_vs_median_pct == 5.0


def test_csv_has_header_and_rows():
    rep = BenchmarkResponse(clinic_id="c", clinic_name="X", city="Almaty",
                            items=[_item(-10, "cheapest")], summary=summarize([_item(-10, "cheapest")]))
    lines = to_csv(rep).strip().splitlines()
    assert lines[0].startswith("service,category,clinic_price_kzt")
    assert "Глюкоза крови" in lines[1] and lines[1].endswith("cheapest")
