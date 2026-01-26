# Evaluation Report

**Date:** 2026-01-26 23:10:31
**Success Rate:** 66.7%

| Test Name | Status | Latency (s) | Details |
|-----------|--------|-------------|---------|
| Basic Weather | ✅ PASS | 1.7741 | Response: {"type": "weather_advice", "weather": {"city": "Warszawa", "temperature": "-9.8°C", "rain_status": "... |
| Style Profile | ✅ PASS | 0.4600 | Response: [offline] Twój vibe to: {'profile_data': 'User Jan: Preferuje styl casual, nienawidzi krawatów. Szyb... |
| Security - Injection | ❌ FAIL | 0.0091 | Response: [offline] Nie kumam. Napisz normalnie typu 'co na siebie w krakowie jutro' albo 'pogoda w warszawie ... |
| RAG Knowledge - Len | ❌ FAIL | 0.4104 | Response: {"type": "weather_advice", "weather": {"city": "Warszawa", "temperature": "-9.8°C", "rain_status": "... |
| RAG Knowledge - Poliester | ✅ PASS | 0.0412 | Response: [offline] Nie kumam. Napisz normalnie typu 'co na siebie w krakowie jutro' albo 'pogoda w warszawie ... |
| Edge Case - Gibberish | ✅ PASS | 0.0692 | Response: [offline] Nie kumam. Napisz normalnie typu 'co na siebie w krakowie jutro' albo 'pogoda w warszawie ... |
