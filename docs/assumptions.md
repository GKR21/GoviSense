# GoviSense System Assumptions & Parameter Registry
**Document ID:** GOVISENSE-DOC-ASSUMPTIONS-2026-V1  
**Project:** ModelX 2.0 Phase 1 (GoviSense)  
**Standard:** Rule 3 Audit Compliance  

All parameters used in backend calculations, optimization models, demand estimations, and simulation engines are catalogued below with physical units, source citations, and governance flags indicating whether officers can adjust them at runtime.

---

## 1. Supply Pressure & SPI Parameters

| Parameter Key | Default Value | Unit | Source / Citation | Officer Adjustable? | Notes |
|---|---|---|---|---|---|
| `spi_ratio_glut_threshold` | 1.20 | Ratio ($S/D$) | Proposal Section 6; Harti Market Outlook | Yes (via `/api/simulate`) | Supply exceeding 120% of projected demand triggers Glut actions |
| `spi_ratio_shortage_threshold` | 0.80 | Ratio ($S/D$) | Proposal Section 6; Harti Market Outlook | Yes (via `/api/simulate`) | Supply falling below 80% of projected demand triggers Shortage actions |
| `spi_glut_threshold` | +0.15 | Delta $((S-D)/D)$ | Historical wholesale price divergence analysis | Yes (via `/api/simulate`) | Secondary metric corresponding to ratio band |
| `spi_shortage_threshold` | -0.15 | Delta $((S-D)/D)$ | Historical wholesale price divergence analysis | Yes (via `/api/simulate`) | Secondary metric corresponding to ratio band |
| `unreported_area_ratio_min` | 0.10 | Ratio (10%) | DOA Agricultural Statistics Unit (ASU) Smallholder Estimation | Yes | Unnotified smallholder plots (< 0.25 ac) |
| `unreported_area_ratio_max` | 0.25 | Ratio (25%) | HARTI Market Research Division (MRD) Unregistered Plots Survey | Yes | Upper bound during peak Maha/Yala planting |
| `post_harvest_loss_big_onion` | 0.15 | Ratio (15%) | HARTI Post-Harvest Loss Research Report No. 142 | Yes | Storage, handling and sorting decay |
| `post_harvest_loss_chilli` | 0.12 | Ratio (12%) | DOA Vegetable Post-Harvest Manual | Yes | Desiccation and transit rot |
| `post_harvest_loss_red_onion` | 0.15 | Ratio (15%) | HARTI Research Report No. 142 | Yes | Field drying and bulb rot |
| `post_harvest_loss_potato` | 0.10 | Ratio (10%) | DOA Horticultural Crop Bulletin | Yes | Cold chain & transit damage |

---

## 2. Decision Optimizer & Gap Parameters (A4)

| Parameter Key | Default Value | Unit | Source / Citation | Officer Adjustable? | Notes |
|---|---|---|---|---|---|
| `import_lead_time_weeks.big_onion` | 7 | Weeks | CBSL / Sri Lanka Ports Authority (SLPA) Trade Bulletin | Yes (via `/api/simulate`) | Transit from Nashik/Tuticorin + quarantine clearance |
| `import_lead_time_weeks.potato` | 6 | Weeks | CBSL / SLPA Trade Bulletin | Yes (via `/api/simulate`) | Transit from Pakistan/India + customs release |
| `import_lead_time_weeks.chilli` | 6 | Weeks | CBSL / SLPA Trade Bulletin | Yes (via `/api/simulate`) | Dry chilli shipment from Guntur |
| `import_lead_time_weeks.red_onion` | 6 | Weeks | CBSL / SLPA Trade Bulletin | Yes (via `/api/simulate`) | Regional import lead time |
| `storage_cost_rs_per_mt_month.big_onion` | 4,500.0 | LKR / MT / month | HARTI Cold Storage & Ventilated Shed Economics 2023 | Yes | Traditional thatched ventilated storage shed |
| `storage_cost_rs_per_mt_month.chilli` | 6,000.0 | LKR / MT / month | HARTI Cold Storage Economics 2023 | Yes | Controlled humidity dry storage |
| `storage_cost_rs_per_mt_month.red_onion` | 5,000.0 | LKR / MT / month | HARTI Cold Storage Economics 2023 | Yes | Ventilated onion store |
| `storage_cost_rs_per_mt_month.potato` | 4,000.0 | LKR / MT / month | Nuwara Eliya Cold Store commercial rate | Yes | Commercial potato chill store |
| `transport_cost_rs_per_mt_km` | 45.0 | LKR / MT / km | National Transport Commission Freight Tariff Schedule 2025 | Yes | Truck haulage to Dambulla Dedicated Economic Centre |
| `distance_to_dambulla_km.Anuradhapura` | 65.0 | km | Road Development Authority (RDA) A9 Highway Distance Table | No | Hub distance from central collection point |
| `distance_to_dambulla_km.Matale` | 45.0 | km | RDA A9 Highway Distance Table | No | Hub distance from Matale collection |
| `cif_colombo_rs_per_mt.big_onion` | 140,000.0 | LKR / MT | Sri Lanka Customs Import Statistics (HS 0703.10) 2025 | Yes | Landed CIF Colombo |
| `cif_colombo_rs_per_mt.chilli` | 420,000.0 | LKR / MT | Sri Lanka Customs Import Statistics (HS 0904.21) 2025 | Yes | Landed CIF Colombo dry chilli |
| `cif_colombo_rs_per_mt.red_onion` | 210,000.0 | LKR / MT | Sri Lanka Customs Import Statistics 2025 | Yes | Regional landed import CIF |
| `cif_colombo_rs_per_mt.potato` | 180,000.0 | LKR / MT | Sri Lanka Customs Import Statistics (HS 0701.90) 2025 | Yes | Landed CIF Colombo table potato |
| `import_tariff_rs_per_mt.big_onion` | 50,000.0 | LKR / MT | Ministry of Finance Special Commodity Levy (SCL) Gazettes | Yes (by Officer) | SCL duty (Rs. 50/kg) |
| `import_tariff_rs_per_mt.chilli` | 150,000.0 | LKR / MT | Ministry of Finance SCL Gazettes | Yes (by Officer) | SCL duty (Rs. 150/kg) |
| `import_tariff_rs_per_mt.red_onion` | 60,000.0 | LKR / MT | Ministry of Finance SCL Gazettes | Yes (by Officer) | SCL duty (Rs. 60/kg) |
| `import_tariff_rs_per_mt.potato` | 50,000.0 | LKR / MT | Ministry of Finance SCL Gazettes | Yes (by Officer) | SCL duty (Rs. 50/kg) |
| `unmet_demand_penalty_rs_per_mt.big_onion` | 350,000.0 | LKR / MT | DCS / HARTI Consumer Welfare Loss Estimation | Yes | Economic shadow cost of consumer shortage spike |
| `unmet_demand_penalty_rs_per_mt.chilli` | 900,000.0 | LKR / MT | DCS / HARTI Consumer Welfare Loss Estimation | Yes | Severe consumer staple basket penalty |
| `unmet_demand_penalty_rs_per_mt.red_onion` | 450,000.0 | LKR / MT | DCS / HARTI Consumer Welfare Loss Estimation | Yes | Welfare penalty |
| `unmet_demand_penalty_rs_per_mt.potato` | 380,000.0 | LKR / MT | DCS / HARTI Consumer Welfare Loss Estimation | Yes | Welfare penalty |

---

## 3. Allocation & Stop Rule Parameters (A1)

| Parameter Key | Default Value | Unit | Source / Citation | Officer Adjustable? | Notes |
|---|---|---|---|---|---|
| `allocation_change_cap_pct` | 0.30 | Ratio (30%) | Proposal Section 6 (A1 Allocation Constraint) | Yes | Maximum allowed change in acreage from previous season |
| `max_farmer_single_crop_share` | 0.60 | Ratio (60%) | Department of Agriculture Farm Diversification Policy | Yes | Farmer cannot put >60% of land into a single monoculture |
| `oversupply_stop_rule_threshold` | 1.10 | Ratio (110%) | Proposal Section 6 / Day 5 Stop Rule | No (Core Guardrail) | When reported acreage reaches 110% of target, remaining recommended acreage drops to 0 |
| `seeded_hash_salt` | `"govisense_maha_yala_v1"` | String | Cryptographic audit deterministic assignment specification | No | Ensures reproducibility across 10,000 simulated farmer calls |

---

## 4. Retail Price Modeling (A2)

| Parameter Key | Default Value | Unit | Source / Citation | Officer Adjustable? | Notes |
|---|---|---|---|---|---|
| `transport_markup_rs_kg` | 12.0 | LKR / kg | CBSL Weekly Economic Indicators / DEC transport differentials | Yes | Fuel and truck haulage markup wholesale-to-retail |
| `retail_margin_ratio` | 0.18 | Ratio (18%) | CBSL / HARTI retail vs Pettah/Dambulla wholesale series | Yes | Calibrated retail overhead and retailer margin (NOT static 1.35x) |

