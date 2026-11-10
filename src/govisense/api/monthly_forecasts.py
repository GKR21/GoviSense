"""Monthly model estimates for available data periods, not future extrapolations."""


def build_monthly_series(rows, model, spi_engine, crop):
    points = []
    for row in rows:
        prediction = model.predict_row(row)
        pressure = spi_engine.compute_spi(
            crop=crop,
            forecast_supply_mt=prediction.point_forecast,
            month=int(row["month"]),
            target_date=str(row["year_month"]),
            import_volume_mt=float(row.get("import_volume_mt", 0.0)),
        )
        # Use the SPI engine's mid-scenario supply, including its loss/import
        # assumptions, so the displayed supply/demand agree with the SPI ratio.
        mid = pressure.scenarios["mid"]
        points.append({
            "period": str(row["year_month"]),
            "supply_mt": mid.supply_mt,
            "demand_mt": mid.demand_mt,
            "spi_ratio": mid.spi_ratio,
        })
    return points
