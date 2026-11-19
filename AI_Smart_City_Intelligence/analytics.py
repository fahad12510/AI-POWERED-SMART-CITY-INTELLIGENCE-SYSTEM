import numpy as np

TRAFFIC_THRESHOLD = 1500
AQI_THRESHOLD = 150
Z_SCORE_THRESHOLD = 2.0

def _arrays(data):
    locations = np.array(data["locations"], dtype=str)
    traffic = np.array(data["traffic"], dtype=float)
    aqi = np.array(data["aqi"], dtype=float)
    return locations, traffic, aqi

def _stats(arr):
    return {
        "mean": round(float(np.mean(arr)), 2),
        "median": round(float(np.median(arr)), 2),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "std": round(float(np.std(arr)), 2),
        "percentile_75": round(float(np.percentile(arr, 75)), 2),
        "ndim": int(arr.ndim),
        "shape": list(arr.shape),
        "size": int(arr.size)
    }

def dashboard_summary(data):
    loc, traffic, aqi = _arrays(data)
    traffic_avg = traffic.mean(axis=1)
    aqi_avg = aqi.mean(axis=1)
    hi_t = int(np.sum(traffic > TRAFFIC_THRESHOLD))
    hi_a = int(np.sum(aqi > AQI_THRESHOLD))
    return {
        "locations_count": int(len(loc)),
        "average_traffic": round(float(traffic.mean()), 1),
        "average_aqi": round(float(aqi.mean()), 1),
        "highest_traffic_location": str(loc[int(np.argmax(traffic_avg))]),
        "highest_aqi_location": str(loc[int(np.argmax(aqi_avg))]),
        "high_traffic_readings": hi_t,
        "high_aqi_readings": hi_a,
        "locations": loc.tolist(),
        "traffic_averages": np.round(traffic_avg, 1).tolist(),
        "aqi_averages": np.round(aqi_avg, 1).tolist(),
        "days": [f"Day {i}" for i in range(1, traffic.shape[1] + 1)],
        "sample_data": bool(data.get("is_sample", True))
    }

def series_data(data, metric):
    loc, traffic, aqi = _arrays(data)
    arr = traffic if metric == "traffic" else aqi
    return {"locations": loc.tolist(), "days": [f"Day {i}" for i in range(1, arr.shape[1]+1)],
            "datasets": [{"label": str(loc[i]), "data": arr[i].tolist()} for i in range(len(loc))]}

def full_analytics(data):
    loc, traffic, aqi = _arrays(data)
    t_avg, a_avg = traffic.mean(axis=1), aqi.mean(axis=1)
    t_order, a_order = np.argsort(t_avg)[::-1], np.argsort(a_avg)[::-1]
    anomalies = []
    for metric, arr, threshold in [("Traffic", traffic, TRAFFIC_THRESHOLD), ("AQI", aqi, AQI_THRESHOLD)]:
        mean, std = arr.mean(), arr.std()
        z = np.zeros_like(arr) if std == 0 else (arr - mean) / std
        mask = (arr > threshold) | (np.abs(z) > Z_SCORE_THRESHOLD)
        for r, c in np.argwhere(mask):
            reason = f"Above threshold ({threshold})" if arr[r, c] > threshold else f"Z-score {z[r,c]:.2f} exceeds ±{Z_SCORE_THRESHOLD}"
            anomalies.append({"metric": metric, "location": str(loc[r]), "day": int(c+1),
                              "value": float(arr[r,c]), "reason": reason})
    return {
        "traffic_stats": _stats(traffic), "aqi_stats": _stats(aqi),
        "total_traffic_by_location": {str(loc[i]): int(traffic[i].sum()) for i in range(len(loc))},
        "average_aqi_by_location": {str(loc[i]): round(float(a_avg[i]), 2) for i in range(len(loc))},
        "daily_average_traffic": np.round(traffic.mean(axis=0), 2).tolist(),
        "daily_average_aqi": np.round(aqi.mean(axis=0), 2).tolist(),
        "traffic_rank": [{"location": str(loc[i]), "average": round(float(t_avg[i]),2)} for i in t_order],
        "aqi_rank": [{"location": str(loc[i]), "average": round(float(a_avg[i]),2)} for i in a_order],
        "anomalies": anomalies,
        "traffic_percentage_change": np.round((traffic[:,1:] - traffic[:,:-1]) / np.maximum(traffic[:,:-1], 1) * 100, 2).tolist(),
        "traffic_growth_scenario_10_percent": np.round(traffic * 1.10, 1).tolist(),
        "thresholds": {"traffic": TRAFFIC_THRESHOLD, "aqi": AQI_THRESHOLD, "z_score": Z_SCORE_THRESHOLD}
    }

def predictions(data):
    loc, traffic, aqi = _arrays(data)
    x = np.arange(1, traffic.shape[1] + 1)
    result = {"note": "Experimental linear estimates based on seven sample days; not reliable operational forecasts.",
              "traffic": [], "aqi": []}
    for i, name in enumerate(loc):
        t = float(np.polyval(np.polyfit(x, traffic[i], 1), len(x)+1))
        a = float(np.polyval(np.polyfit(x, aqi[i], 1), len(x)+1))
        result["traffic"].append({"location": str(name), "history": traffic[i].tolist(),
                                  "estimate": round(max(0,t),1), "trend": "increasing" if t > traffic[i,-1] else "decreasing"})
        result["aqi"].append({"location": str(name), "history": aqi[i].tolist(),
                              "estimate": round(max(0,a),1), "trend": "increasing" if a > aqi[i,-1] else "decreasing"})
    return result
