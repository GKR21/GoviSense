# GoviSense Operational Assumptions & Registry Integration Architecture

**Team DARKBITE · ModelX 2.0 Phase 2**  
**Pilot District: Anuradhapura (Big Onion, Green Chilli)**  
**Target Release: v2.0 Production Pilot**

---

## 1. Farmer Identity, Registry Verification & Future Work (Task 12)

### Current Architecture (Pilot Implementation)
In the current deployment phase, farmer authentication and data ingestion operate under a privacy-preserving pseudonymous protocol:
- **Pseudonymous ID Hashing**: Farmer identities are pseudonymized client-side or during onboarding (e.g., `ANU-FARMER-XXXXX`), ensuring personal identifying information (PII) is decoupled from agronomic reporting.
- **Client & Role Authentication**: Ground submissions are protected via JWT bearer tokens assigned to authenticated farmers or agricultural officers.
- **Local Sliding-Window Rate Limiting**: Ingestion endpoints enforce rate limits (maximum 5 planting reports per 60 seconds per `pseudonymous_id`) to prevent telemetry poisoning, denial-of-service, or automated script spam.
- **Duplicate Report Rejection**: The ingestion engine rejects duplicate planting reports containing identical farmer ID, crop, season, and planted acreage combinations.

### Future Work: Agrarian Services Department National Registry Integration
> [!IMPORTANT]
> **Registry Verification Status: FUTURE WORK (Phase 3 Integration Target)**  
> Direct verification against the national farmer registry maintained by the Department of Agrarian Development (DAD) / Ministry of Agriculture is slated for Phase 3.

Once national API access and memorandum-of-understanding (MOU) clearances are finalized with the Department of Agrarian Development:
1. **National Farmer ID Validation**: Every pseudonymous farmer token will map to an audited DAD Agrarian Services Centre (ASC) register number.
2. **Land Tenure Cross-Referencing**: Land parcel extents (in hectares or acres) will be cross-validated against digital land deed and Govijana Seva paddy/upland registry records to prevent over-reporting.
3. **Fertilizer & Subsidy Quota Reconciliation**: Reported planting areas will link with agrarian service bank accounts for automated subsidy buffer disbursement.

---

## 2. Agronomic & Harvest Supply Assumptions

- **Post-Harvest Loss Fractions**:
  - Big Onion: Baseline loss is assumed at $15\%$ ($\pm 3\%$ depending on storage ventilation).
  - Chilli: Baseline loss is assumed at $12\%$ for green fresh pods; $18\%$ for sun-dried chilli.
- **Crop Duration & Harvest Windows**:
  - Big Onion: 90–110 days duration. Yala peak harvest spread: August ($40\%$), September ($45\%$), October ($15\%$).
  - Chilli: 120–150 days duration. Maha peak harvest spread: January ($35\%$), February ($45\%$), March ($20\%$). Yala peak: July ($35\%$), August ($45\%$), September ($20\%$).
- **Pilot District Contribution**:
  - Anuradhapura represents approximately $50\%$ of national domestic Big Onion production and $40\%$ of commercial green chilli production.

---

## 3. Market & Pricing Mechanics

- **Price Discovery Benchmark**:
  - Dambulla Dedicated Economic Centre (DEC) wholesale prices represent the primary price formation index for the Dry Zone.
  - Pettah Central Wholesale Market prices serve as the urban terminal retail proxy.
- **Farmgate Margin Estimation**:
  - When direct farmgate survey records are unavailable, producer farmgate prices are calibrated at $82\%$ of Dambulla wholesale prices, consistent with HARTI marketing division surveys.
- **Minimum Fair Farmgate Floor**:
  - Big Onion: Rs. 110.00 / kg.
  - Chilli: Rs. 220.00 / kg.

---

## 4. Supply Pressure Index (SPI) Banding

The Supply Pressure Index ratio ($\text{SPI} = \text{Supply} / \text{Demand}$) is categorized into 3 policy bands:
- **Severe Shortage / Shortage**: $\text{SPI} < 0.85$ (Supply deficit $> 15\%$; triggers planting expansion or phased import scheduling).
- **Balanced Market**: $0.85 \le \text{SPI} \le 1.15$ (Equilibrium supply; stable price band).
- **Severe Surplus / Glut**: $\text{SPI} > 1.15$ (Supply surplus $> 15\%$; triggers oversupply stop rules, import permit deferrals, and cold storage buffer retention).

---

## 5. Climatological & Anomaly Baselines

- **Anomalies**:
  - NASA POWER daily solar and agro-climatological data and Open-Meteo ERA5 Land Reanalysis data are benchmarked against the standard 30-year WMO climatological reference normal (1991–2020).
- **Missing Historical Readings**:
  - Missing daily meteorological sensor values are forward-filled up to a maximum contiguous gap of 5 days; longer gaps are interpolated using monthly historical means.

